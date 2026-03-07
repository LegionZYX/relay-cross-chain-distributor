# -*- coding: utf-8 -*-
"""
Relay Cross-Chain Distributor - Web Version
Flask Backend
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from web3 import Web3
from eth_account import Account
import requests
import time
import threading

app = Flask(__name__)
CORS(app)

# 链配置
CHAINS = {
    "Ethereum": {"chain_id": 1, "rpc": "https://eth.llamarpc.com", "explorer": "https://etherscan.io/tx/"},
    "Base": {"chain_id": 8453, "rpc": "https://mainnet.base.org", "explorer": "https://basescan.org/tx/"},
    "BSC": {"chain_id": 56, "rpc": "https://bsc-dataseed.binance.org", "explorer": "https://bscscan.com/tx/"},
    "Arbitrum": {"chain_id": 42161, "rpc": "https://arb1.arbitrum.io/rpc", "explorer": "https://arbiscan.io/tx/"},
    "Optimism": {"chain_id": 10, "rpc": "https://mainnet.optimism.io", "explorer": "https://optimistic.etherscan.io/tx/"},
    "Polygon": {"chain_id": 137, "rpc": "https://polygon-rpc.com", "explorer": "https://polygonscan.com/tx/"},
    "Avalanche": {"chain_id": 43114, "rpc": "https://api.avax.network/ext/bc/C/rpc", "explorer": "https://snowtrace.io/tx/"},
}

RELAY_API = "https://api.relay.link/quote/v2"
NATIVE_TOKEN = "0x0000000000000000000000000000000000000000"

# 全局状态
class AppState:
    def __init__(self):
        self.wallet_address = None
        self.private_key = None
        self.is_connected = False
        self.distribution_results = []
        self.is_sending = False
        self.logs = []
    
    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        if len(self.logs) > 100:
            self.logs.pop(0)
    
    def clear_logs(self):
        self.logs = []

state = AppState()

def get_web3(chain_name):
    """获取 Web3 连接"""
    rpc = CHAINS.get(chain_name, {}).get('rpc')
    if not rpc:
        return None
    return Web3(Web3.HTTPProvider(rpc))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/connect', methods=['POST'])
def connect_wallet():
    """连接钱包"""
    data = request.json
    private_key = data.get('private_key', '').strip()
    
    if not private_key.startswith('0x'):
        private_key = '0x' + private_key
    
    try:
        account = Account.from_key(private_key)
        state.wallet_address = account.address
        state.private_key = private_key
        state.is_connected = True
        state.add_log(f"✅ 钱包已连接：{account.address}")
        
        return jsonify({
            'success': True,
            'address': account.address,
            'message': '钱包连接成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'私钥无效：{str(e)}'
        }), 400

@app.route('/api/disconnect', methods=['POST'])
def disconnect_wallet():
    """断开钱包"""
    state.wallet_address = None
    state.private_key = None
    state.is_connected = False
    state.distribution_results = []
    state.clear_logs()
    state.add_log("已断开连接")
    
    return jsonify({'success': True})

@app.route('/api/balance', methods=['POST'])
def get_balance():
    """获取余额"""
    if not state.is_connected:
        return jsonify({'success': False, 'message': '请先连接钱包'}), 400
    
    data = request.json
    chain = data.get('chain', 'Ethereum')
    
    try:
        w3 = get_web3(chain)
        if not w3 or not w3.is_connected():
            return jsonify({'success': False, 'message': f'无法连接到 {chain}'}), 500
        
        balance_wei = w3.eth.get_balance(state.wallet_address)
        balance_eth = float(w3.from_wei(balance_wei, 'ether'))
        
        return jsonify({
            'success': True,
            'balance': balance_eth,
            'chain': chain
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/quote', methods=['POST'])
def get_quote():
    """获取跨链报价"""
    if not state.is_connected:
        return jsonify({'success': False, 'message': '请先连接钱包'}), 400
    
    data = request.json
    origin_chain = data.get('origin_chain', 'Ethereum')
    dest_chain = data.get('dest_chain', 'BSC')
    amount = data.get('amount', 0.001)
    recipient = data.get('recipient', state.wallet_address)
    
    try:
        payload = {
            "user": recipient,
            "originChainId": CHAINS[origin_chain]["chain_id"],
            "destinationChainId": CHAINS[dest_chain]["chain_id"],
            "originCurrency": NATIVE_TOKEN,
            "destinationCurrency": NATIVE_TOKEN,
            "recipient": recipient,
            "amount": str(int(float(amount) * 10**18)),
            "useDepositAddress": False,
            "refundTo": state.wallet_address,
            "tradeType": "EXACT_INPUT"
        }
        
        response = requests.post(RELAY_API, json=payload, timeout=15)
        
        if response.status_code != 200:
            error_msg = response.json().get('message', 'API 错误')
            return jsonify({'success': False, 'message': error_msg}), 400
        
        quote_data = response.json()
        step = quote_data['steps'][0]
        tx_data = step['items'][0]['data']
        
        return jsonify({
            'success': True,
            'deposit_address': tx_data['to'],
            'value': tx_data['value'],
            'data': tx_data['data'],
            'gas': int(tx_data.get('gas', 200000)),
            'maxFeePerGas': int(tx_data.get('maxFeePerGas', 0)),
            'maxPriorityFeePerGas': int(tx_data.get('maxPriorityFeePerGas', 0)),
            'request_id': step.get('requestId', '')
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_distribution():
    """生成分发计划"""
    if not state.is_connected:
        return jsonify({'success': False, 'message': '请先连接钱包'}), 400
    
    data = request.json
    wallets = data.get('wallets', [])
    amount = data.get('amount', 0.001)
    origin_chain = data.get('origin_chain', 'Ethereum')
    dest_chain = data.get('dest_chain', 'BSC')
    
    if not wallets:
        return jsonify({'success': False, 'message': '请输入目标钱包地址'}), 400
    
    state.distribution_results = []
    state.add_log(f"开始生成分发计划：{len(wallets)} 个钱包")
    
    try:
        for i, wallet in enumerate(wallets):
            if not wallet.startswith('0x'):
                continue
            
            payload = {
                "user": wallet,
                "originChainId": CHAINS[origin_chain]["chain_id"],
                "destinationChainId": CHAINS[dest_chain]["chain_id"],
                "originCurrency": NATIVE_TOKEN,
                "destinationCurrency": NATIVE_TOKEN,
                "recipient": wallet,
                "amount": str(int(float(amount) * 10**18)),
                "useDepositAddress": False,
                "refundTo": state.wallet_address,
                "tradeType": "EXACT_INPUT"
            }
            
            response = requests.post(RELAY_API, json=payload, timeout=15)
            
            if response.status_code == 200:
                quote_data = response.json()
                step = quote_data['steps'][0]
                tx_data = step['items'][0]['data']
                
                state.distribution_results.append({
                    'index': i + 1,
                    'target': wallet,
                    'deposit_address': tx_data['to'],
                    'value': tx_data['value'],
                    'data': tx_data['data'],
                    'gas': int(tx_data.get('gas', 200000)),
                    'maxFeePerGas': int(tx_data.get('maxFeePerGas', 0)),
                    'maxPriorityFeePerGas': int(tx_data.get('maxPriorityFeePerGas', 0)),
                    'send_amount': amount,
                    'origin_chain': origin_chain,
                    'dest_chain': dest_chain
                })
                
                state.add_log(f"✅ [{i+1}/{len(wallets)}] {wallet[:20]}...")
        
        state.add_log(f"✨ 完成！成功 {len(state.distribution_results)}/{len(wallets)} 个")
        
        return jsonify({
            'success': True,
            'count': len(state.distribution_results),
            'results': state.distribution_results
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def execute_transaction(result):
    """执行单笔交易"""
    try:
        w3 = get_web3(result['origin_chain'])
        
        nonce = w3.eth.get_transaction_count(state.wallet_address)
        
        tx = {
            'type': '0x2',
            'nonce': nonce,
            'chainId': CHAINS[result['origin_chain']]['chain_id'],
            'to': Web3.to_checksum_address(result['deposit_address']),
            'value': int(result['value']),
            'data': result['data'],
            'gas': result['gas'],
            'maxFeePerGas': result['maxFeePerGas'],
            'maxPriorityFeePerGas': result['maxPriorityFeePerGas']
        }
        
        signed_tx = w3.eth.account.sign_transaction(tx, state.private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        tx_hash_hex = w3.to_hex(tx_hash)
        
        state.add_log(f"📤 交易已发送：{tx_hash_hex[:30]}...")
        
        receipt = None
        for _ in range(36):
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    break
            except:
                pass
            time.sleep(5)
        
        if receipt and receipt['status'] == 1:
            actual_gas = receipt['gasUsed']
            actual_gas_eth = float(w3.from_wei(actual_gas * result['maxFeePerGas'], 'ether'))
            
            result['tx_hash'] = tx_hash_hex
            result['status'] = 'success'
            result['block_number'] = receipt['blockNumber']
            result['gas_used'] = actual_gas
            result['actual_gas_eth'] = actual_gas_eth
            result['explorer_url'] = CHAINS[result['origin_chain']]['explorer'] + tx_hash_hex
            
            state.add_log(f"✅ 交易成功！Gas: {actual_gas_eth:.6f} ETH")
        else:
            result['status'] = 'failed'
            result['tx_hash'] = tx_hash_hex
            state.add_log(f"❌ 交易失败")
        
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        state.add_log(f"❌ 错误：{e}")

@app.route('/api/execute', methods=['POST'])
def execute_sending():
    """执行发送"""
    if not state.is_connected:
        return jsonify({'success': False, 'message': '请先连接钱包'}), 400
    
    if not state.distribution_results:
        return jsonify({'success': False, 'message': '请先生成分发计划'}), 400
    
    if state.is_sending:
        return jsonify({'success': False, 'message': '正在发送中，请等待'}), 400
    
    state.is_sending = True
    state.add_log("=" * 60)
    state.add_log("💸 开始执行跨链发送...")
    
    def run_execution():
        success_count = 0
        failed_count = 0
        
        for i, result in enumerate(state.distribution_results):
            execute_transaction(result)
            
            if result.get('status') == 'success':
                success_count += 1
            else:
                failed_count += 1
            
            if i < len(state.distribution_results) - 1:
                time.sleep(10)
        
        state.is_sending = False
        state.add_log("=" * 60)
        state.add_log(f"🎉 发送完成！成功：{success_count} | 失败：{failed_count}")
    
    thread = threading.Thread(target=run_execution)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': '开始执行发送'
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """获取执行状态"""
    return jsonify({
        'is_connected': state.is_connected,
        'wallet_address': state.wallet_address,
        'distribution_count': len(state.distribution_results),
        'is_sending': state.is_sending,
        'logs': state.logs[-20:]
    })

@app.route('/api/results', methods=['GET'])
def get_results():
    """获取结果"""
    return jsonify({
        'results': state.distribution_results
    })

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """获取日志"""
    return jsonify({
        'logs': state.logs[-50:]
    })

if __name__ == '__main__':
    print("=" * 60)
    print("  Relay Cross-Chain Distributor - Web Version")
    print("=" * 60)
    print("\n  访问地址：http://localhost:5000")
    print("\n" + "=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
