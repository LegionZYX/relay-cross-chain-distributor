# -*- coding: utf-8 -*-
"""
Relay 跨链分发钱包 - 完整修复版
修复问题:
1. Checksum 地址问题
2. API 错误处理优化
3. 添加详细的错误日志
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import threading
import time
import random
from datetime import datetime
import requests
from eth_account import Account
from web3 import Web3
from web3.exceptions import TransactionNotFound

# 链配置（包含 RPC 节点）
DEFAULT_CHAINS = {
    "Ethereum": {
        "chain_id": 1, 
        "name": "ETH",
        "rpc": "https://eth.llamarpc.com",
        "explorer": "https://etherscan.io/tx/"
    },
    "Base": {
        "chain_id": 8453, 
        "name": "ETH",
        "rpc": "https://mainnet.base.org",
        "explorer": "https://basescan.org/tx/"
    },
    "BSC": {
        "chain_id": 56, 
        "name": "BNB",
        "rpc": "https://bsc-dataseed.binance.org",
        "explorer": "https://bscscan.com/tx/"
    },
    "Arbitrum": {
        "chain_id": 42161, 
        "name": "ETH",
        "rpc": "https://arb1.arbitrum.io/rpc",
        "explorer": "https://arbiscan.io/tx/"
    },
    "Optimism": {
        "chain_id": 10, 
        "name": "ETH",
        "rpc": "https://mainnet.optimism.io",
        "explorer": "https://optimistic.etherscan.io/tx/"
    },
    "Polygon": {
        "chain_id": 137, 
        "name": "MATIC",
        "rpc": "https://polygon-rpc.com",
        "explorer": "https://polygonscan.com/tx/"
    },
    "Avalanche": {
        "chain_id": 43114, 
        "name": "AVAX",
        "rpc": "https://api.avax.network/ext/bc/C/rpc",
        "explorer": "https://snowtrace.io/tx/"
    },
}

# Token 合约地址
TOKEN_ADDRESSES = {
    "USDC": {
        "Ethereum": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "Base": "0x833589fcd6edb6e08f4c7c32d4f71b54bda02913",
        "BSC": "0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d",
        "Arbitrum": "0xaf88d065e77c8cc2239327c5edb3a432268e5831",
    },
    "USDT": {
        "Ethereum": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "Base": "0xfde4c96c8593536e31f229ea8f37b2ada2699bb2",
        "BSC": "0x55d398326f99059ff775485246999027b3197955",
    },
}

NATIVE_TOKEN = "0x0000000000000000000000000000000000000000"


class CrossChainDistributor:
    def __init__(self, root):
        self.root = root
        self.root.title("🔗 Relay 跨链分发钱包 - 修复版")
        self.root.geometry("1000x700")
        
        self.wallet_address = None
        self.private_key = None
        self.is_connected = False
        self.distribution_results = []
        self.price_cache = {}
        self.price_cache_time = {}
        self.is_calculating = False
        self.web3_connections = {}
        self.is_sending = False
        
        # 创建滚动区域
        self.create_scrollable_ui()
        
        # 从 API 加载链
        self.load_chains_from_api()
    
    def create_scrollable_ui(self):
        """创建可滚动的 UI"""
        # 主框架
        main_container = ttk.Frame(self.root)
        main_container.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # 创建 Canvas 和滚动条
        canvas = tk.Canvas(main_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        # 可滚动框架
        self.scroll_frame = ttk.Frame(canvas)
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 鼠标滚轮支持
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        main_container.columnconfigure(0, weight=1)
        main_container.rowconfigure(0, weight=1)
        
        # 构建 UI
        self.setup_ui()
    
    def setup_ui(self):
        """构建 UI 界面"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        
        parent = self.scroll_frame
        padding = 10
        
        # ===== 1. 钱包连接 =====
        wallet_frame = ttk.LabelFrame(parent, text="💼 钱包连接", padding=padding)
        wallet_frame.grid(row=0, column=0, sticky="we", padx=10, pady=5)
        
        self.wallet_status_label = ttk.Label(wallet_frame, text="❌ 未连接", foreground="red", font=('Arial', 11, 'bold'))
        self.wallet_status_label.grid(row=0, column=0, padx=5)
        
        self.wallet_addr_display = ttk.Label(wallet_frame, text="", width=50)
        self.wallet_addr_display.grid(row=0, column=1, padx=5)
        
        ttk.Button(wallet_frame, text="🔑 私钥导入", command=self.import_private_key).grid(row=0, column=2, padx=5)
        
        # ===== 2. 链配置 =====
        chain_frame = ttk.LabelFrame(parent, text="⛓️ 链配置", padding=padding)
        chain_frame.grid(row=1, column=0, sticky="we", padx=10, pady=5)
        
        # ===== 3. 金额和兑换 =====
        amount_frame = ttk.LabelFrame(parent, text="💰 金额和兑换", padding=padding)
        amount_frame.grid(row=2, column=0, sticky="we", padx=10, pady=5)
        
        # 分发模式
        ttk.Label(amount_frame, text="分发模式:").grid(row=0, column=0, padx=5)
        self.amount_mode_var = tk.StringVar(value="single")
        mode_frame = ttk.Frame(amount_frame)
        mode_frame.grid(row=0, column=1, padx=5)
        ttk.Radiobutton(mode_frame, text="按单个金额", variable=self.amount_mode_var, 
                       value="single", command=self.on_amount_mode_change).grid(row=0, column=0, padx=5)
        ttk.Radiobutton(mode_frame, text="按总金额", variable=self.amount_mode_var,
                       value="total", command=self.on_amount_mode_change).grid(row=0, column=1, padx=5)
        
        ttk.Label(amount_frame, text="钱包数量:").grid(row=0, column=2, padx=15)
        self.wallet_count_var = tk.StringVar(value="5")
        wallet_count_entry = ttk.Entry(amount_frame, textvariable=self.wallet_count_var, width=8)
        wallet_count_entry.grid(row=0, column=3, padx=5)
        
        # 支付 Token 金额
        pay_frame = ttk.Frame(amount_frame)
        pay_frame.grid(row=1, column=0, columnspan=10, sticky="w", pady=8)
        
        ttk.Label(pay_frame, text="💵 支付:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5)
        self.pay_single_var = tk.StringVar(value="0.005")
        ttk.Label(pay_frame, text="单个:").grid(row=0, column=1, padx=5)
        self.pay_single_entry = ttk.Entry(pay_frame, textvariable=self.pay_single_var, width=15)
        self.pay_single_entry.grid(row=0, column=2, padx=5)
        
        ttk.Label(pay_frame, text="总计:").grid(row=0, column=3, padx=5)
        self.pay_total_var = tk.StringVar(value="")
        self.pay_total_entry = ttk.Entry(pay_frame, textvariable=self.pay_total_var, width=15, state='disabled')
        self.pay_total_entry.grid(row=0, column=4, padx=5)
        
        # 接收 Token 金额
        receive_frame = ttk.Frame(amount_frame)
        receive_frame.grid(row=2, column=0, columnspan=10, sticky="w", pady=5)
        
        ttk.Label(receive_frame, text="💰 接收:", font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5)
        self.receive_single_var = tk.StringVar(value="--")
        ttk.Label(receive_frame, text="单个:").grid(row=0, column=1, padx=5)
        self.receive_single_label = ttk.Label(receive_frame, textvariable=self.receive_single_var, 
                                             foreground="green", font=('Arial', 10, 'bold'), width=18, anchor='w')
        self.receive_single_label.grid(row=0, column=2, padx=5)
        
        self.receive_total_var = tk.StringVar(value="--")
        ttk.Label(receive_frame, text="总计:").grid(row=0, column=3, padx=5)
        self.receive_total_label = ttk.Label(receive_frame, textvariable=self.receive_total_var, 
                                            foreground="green", font=('Arial', 10, 'bold'), width=18, anchor='w')
        self.receive_total_label.grid(row=0, column=4, padx=5)
        
        # ===== 4. 目标钱包 =====
        target_frame = ttk.LabelFrame(parent, text="📋 目标钱包列表", padding=padding)
        target_frame.grid(row=3, column=0, sticky="we", padx=10, pady=5)
        
        self.target_text = scrolledtext.ScrolledText(target_frame, height=6, width=80)
        self.target_text.grid(row=0, column=0, columnspan=4, padx=5, pady=5)
        
        ttk.Button(target_frame, text="📂 加载文件", command=self.load_wallets_file).grid(row=1, column=0, padx=5)
        ttk.Button(target_frame, text="📋 粘贴示例", command=self.paste_example).grid(row=1, column=1, padx=5)
        ttk.Button(target_frame, text="🗑️ 清空", command=self.clear_wallets).grid(row=1, column=2, padx=5)
        
        self.count_label = ttk.Label(target_frame, text="数量：0", font=('Arial', 10, 'bold'))
        self.count_label.grid(row=1, column=3, padx=10)
        
        # ===== 5. 退款地址 =====
        refund_frame = ttk.LabelFrame(parent, text="💰 退款地址", padding=padding)
        refund_frame.grid(row=4, column=0, sticky="we", padx=10, pady=5)
        
        self.refund_addr_var = tk.StringVar()
        ttk.Entry(refund_frame, textvariable=self.refund_addr_var, width=60).grid(row=0, column=0, padx=5)
        ttk.Button(refund_frame, text="使用当前钱包", command=self.use_current_wallet).grid(row=0, column=1, padx=5)
        
        # ===== 6. 操作按钮 =====
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=5, column=0, pady=15)
        
        ttk.Button(button_frame, text="🔍 测试 API", command=self.test_api).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="🚀 生成分发计划", command=self.generate_distribution).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="💸 执行发送", command=self.execute_sending).grid(row=0, column=2, padx=10)
        ttk.Button(button_frame, text="💾 导出结果", command=self.export_results).grid(row=0, column=3, padx=10)
        
        # ===== 7. 日志 =====
        log_frame = ttk.LabelFrame(parent, text="📝 执行日志", padding=padding)
        log_frame.grid(row=6, column=0, sticky="we", padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, width=80)
        self.log_text.grid(row=0, column=0, padx=5, pady=5)
        
        # ===== 8. 进度条 =====
        self.progress = ttk.Progressbar(parent, mode='determinate', length=900)
        self.progress.grid(row=7, column=0, padx=10, pady=5)
        
        self.progress_label = ttk.Label(parent, text="就绪", font=('Arial', 10, 'bold'))
        self.progress_label.grid(row=8, column=0, padx=10, pady=5)
        
        # 初始化
        self.on_chain_change()
        self.calculate_exchange()
    
    def log(self, message):
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def import_private_key(self):
        """导入私钥"""
        win = tk.Toplevel(self.root)
        win.title("私钥导入")
        win.geometry("450x200")
        win.resizable(False, False)
        
        ttk.Label(win, text="🔑 私钥导入", font=('Arial', 14, 'bold')).pack(pady=10)
        ttk.Label(win, text="私钥:").pack()
        
        pk_entry = ttk.Entry(win, width=60, show="*")
        pk_entry.pack(pady=5)
        
        def do_import():
            pk = pk_entry.get().strip()
            if not pk.startswith("0x"):
                pk = "0x" + pk
            try:
                account = Account.from_key(pk)
                self.wallet_address = account.address
                self.private_key = pk
                self.is_connected = True
                
                self.wallet_status_label.config(text="✅ 已连接", foreground="green")
                self.wallet_addr_display.config(text=f"{self.wallet_address[:10]}...{self.wallet_address[-8:]}")
                self.refund_addr_var.set(self.wallet_address)
                
                self.log(f"✅ 钱包已连接：{self.wallet_address}")
                win.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"私钥无效：{e}")
        
        ttk.Button(win, text="导入", command=do_import).pack(pady=10)
        ttk.Label(win, text="⚠️ 私钥仅存储在内存中，关闭程序即清除", foreground="red", font=('Arial', 9)).pack()
    
    def load_chains_from_api(self):
        """从 API 加载支持的链"""
        def fetch():
            try:
                response = requests.get("https://api.relay.link/chains", timeout=10)
                data = response.json()
                
                chains = [c['displayName'] for c in data.get('chains', []) if c.get('displayName')]
                if chains:
                    self.root.after(0, lambda: [self.origin_combo.config(values=chains), 
                                               self.dest_combo.config(values=chains)])
                    self.log(f"✅ 已加载 {len(chains)} 条链")
            except Exception as e:
                self.log(f"⚠️ 链加载失败：{e}")
        
        threading.Thread(target=fetch, daemon=True).start()
    
    def on_chain_change(self):
        """链改变时的处理"""
        dest_chain = self.dest_chain_var.get()
        # 自动设置接收 Token
        if dest_chain == "BSC":
            self.receive_token_var.set("BNB")
        elif dest_chain == "Polygon":
            self.receive_token_var.set("MATIC")
        elif dest_chain == "Avalanche":
            self.receive_token_var.set("AVAX")
        else:
            self.receive_token_var.set("ETH")
        
        self.log(f"📍 路径：{self.origin_chain_var.get()} → {dest_chain}")
        self.calculate_exchange()
    
    def on_amount_mode_change(self):
        """切换金额模式"""
        mode = self.amount_mode_var.get()
        if mode == "total":
            self.pay_single_entry.config(state='disabled')
            self.pay_total_entry.config(state='normal')
        else:
            self.pay_single_entry.config(state='normal')
            self.pay_total_entry.config(state='disabled')
        self.calculate_exchange()
    
    def calculate_exchange(self):
        """计算兑换金额"""
        if self.is_calculating:
            return
        self.is_calculating = True
        
        try:
            count = int(self.wallet_count_var.get()) if self.wallet_count_var.get() else 1
            if count <= 0:
                count = 1
            
            mode = self.amount_mode_var.get()
            if mode == "total":
                try:
                    pay_total = float(self.pay_total_var.get()) if self.pay_total_var.get() else 0
                    if count > 0 and pay_total > 0:
                        self.pay_single_var.set(f"{pay_total/count:.6f}")
                except:
                    pass
            else:
                try:
                    pay_single = float(self.pay_single_var.get()) if self.pay_single_var.get() else 0
                    if count > 0 and pay_single > 0:
                        self.pay_total_var.set(f"{pay_single*count:.6f}")
                except:
                    pass
            
            # 获取价格
            pay_token = self.token_var.get()
            if pay_token == "Native":
                pay_chain = self.origin_chain_var.get()
                pay_symbol = DEFAULT_CHAINS.get(pay_chain, {}).get('name', 'ETH')
            else:
                pay_symbol = pay_token
            
            receive_token = self.receive_token_var.get()
            if receive_token == "Native":
                receive_chain = self.dest_chain_var.get()
                receive_symbol = DEFAULT_CHAINS.get(receive_chain, {}).get('name', 'ETH')
            else:
                receive_symbol = receive_token
            
            pay_price = self.get_token_price(pay_symbol)
            receive_price = self.get_token_price(receive_symbol)
            
            if pay_price:
                self.pay_price_label.config(text=f"💵 ${pay_price:,.2f}")
            if receive_price:
                self.receive_price_label.config(text=f"💵 ${receive_price:,.2f}")
            
            # 计算接收金额
            pay_single = float(self.pay_single_var.get()) if self.pay_single_var.get() else 0
            
            if pay_price and receive_price and pay_single > 0:
                fee_rate = 0.005
                receive_single = (pay_single * pay_price / receive_price) * (1 - fee_rate)
                receive_total = receive_single * count
                
                self.receive_single_var.set(f"{receive_single:.6f} {receive_symbol}")
                self.receive_total_var.set(f"{receive_total:.6f} {receive_symbol}")
                
                rate = pay_price / receive_price if receive_price > 0 else 0
                self.exchange_rate_label.config(text=f"💱 1 {pay_symbol} ≈ {rate:.4f} {receive_symbol} (0.5%)")
            else:
                self.receive_single_var.set("--")
                self.receive_total_var.set("--")
                self.exchange_rate_label.config(text="💱 --")
                
        except:
            pass
        finally:
            self.is_calculating = False
    
    def get_token_price(self, symbol):
        """获取 Token 价格（带缓存）"""
        import time
        
        cache_key = symbol.upper()
        current = time.time()
        
        if cache_key in self.price_cache:
            if current - self.price_cache_time.get(cache_key, 0) < 30:
                return self.price_cache[cache_key]
        
        try:
            coin_ids = {'ETH': 'ethereum', 'BNB': 'binancecoin', 'MATIC': 'matic-network', 
                       'AVAX': 'avalanche-2', 'USDC': 'usd-coin', 'USDT': 'tether'}
            
            coin_id = coin_ids.get(cache_key)
            if not coin_id:
                return None
            
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
            r = requests.get(url, timeout=3)
            data = r.json()
            
            if coin_id in data and 'usd' in data[coin_id]:
                price = data[coin_id]['usd']
                self.price_cache[cache_key] = price
                self.price_cache_time[cache_key] = current
                return price
        except:
            pass
        
        return None
    
    def get_web3_connection(self, chain_name):
        """获取 Web3 连接（带缓存）"""
        if chain_name not in self.web3_connections:
            rpc_url = DEFAULT_CHAINS.get(chain_name, {}).get('rpc')
            if not rpc_url:
                raise ValueError(f"未找到 {chain_name} 的 RPC 配置")
            
            w3 = Web3(Web3.HTTPProvider(rpc_url))
            if not w3.is_connected():
                raise ValueError(f"无法连接到 {chain_name} 的 RPC 节点")
            
            self.web3_connections[chain_name] = w3
        
        return self.web3_connections[chain_name]
    
    def estimate_gas(self, w3, from_addr, to_address, value_wei):
        """估算 gas 费用并优化"""
        try:
            gas_price = w3.eth.gas_price
            
            # 将地址转换为 checksum 格式
            to_checksum = Web3.to_checksum_address(to_address)
            from_checksum = Web3.to_checksum_address(from_addr)
            
            gas_limit = w3.eth.estimate_gas({
                'from': from_checksum,
                'to': to_checksum,
                'value': value_wei
            })
            
            gas_limit = int(gas_limit * 1.2)
            
            max_gas_price = w3.to_wei(50, 'gwei')
            if gas_price > max_gas_price:
                gas_price = max_gas_price
            
            total_gas_cost = gas_limit * gas_price
            
            return {
                'gas_limit': gas_limit,
                'gas_price': gas_price,
                'total_cost_wei': total_gas_cost,
                'total_cost_eth': w3.from_wei(total_gas_cost, 'ether')
            }
        except Exception as e:
            raise ValueError(f"Gas 估算失败：{e}")
    
    def send_transaction(self, chain_name, to_address, amount_wei):
        """构建、签名并发送交易 - 修复 checksum 地址"""
        try:
            w3 = self.get_web3_connection(chain_name)
            
            if not self.private_key:
                raise ValueError("未导入私钥")
            
            from_address = self.wallet_address
            
            # 将地址转换为 checksum 格式
            to_checksum = Web3.to_checksum_address(to_address)
            from_checksum = Web3.to_checksum_address(from_address)
            
            gas_info = self.estimate_gas(w3, from_address, to_address, amount_wei)
            
            nonce = w3.eth.get_transaction_count(from_checksum)
            
            tx = {
                'nonce': nonce,
                'to': to_checksum,
                'value': amount_wei,
                'gas': gas_info['gas_limit'],
                'gasPrice': gas_info['gas_price'],
                'chainId': DEFAULT_CHAINS[chain_name]['chain_id']
            }
            
            signed_tx = w3.eth.account.sign_transaction(tx, self.private_key)
            
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_hash_hex = w3.to_hex(tx_hash)
            
            self.log(f"📤 交易已发送：{tx_hash_hex[:20]}...")
            
            receipt = self.wait_for_transaction_receipt(w3, tx_hash)
            
            if receipt and receipt['status'] == 1:
                return {
                    'success': True,
                    'tx_hash': tx_hash_hex,
                    'gas_used': receipt['gasUsed'],
                    'block_number': receipt['blockNumber'],
                    'explorer_url': DEFAULT_CHAINS[chain_name]['explorer'] + tx_hash_hex
                }
            else:
                return {
                    'success': False,
                    'tx_hash': tx_hash_hex,
                    'error': 'Transaction failed'
                }
                
        except Exception as e:
            error_msg = str(e)
            self.log(f"❌ 发送失败：{error_msg}")
            return {
                'success': False,
                'error': error_msg
            }
    
    def wait_for_transaction_receipt(self, w3, tx_hash, timeout=120):
        """等待交易确认"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    return receipt
            except TransactionNotFound:
                pass
            except Exception:
                pass
            
            time.sleep(2)
        
        return None
    
    def test_api(self):
        """测试 API"""
        if not self.is_connected:
            messagebox.showwarning("警告", "请先连接钱包")
            return
        
        self.log("🔍 测试 API...")
        try:
            recipient = self.wallet_address
            amount = float(self.pay_single_var.get())
            
            payload = {
                "user": recipient,
                "originChainId": DEFAULT_CHAINS[self.origin_chain_var.get()]["chain_id"],
                "destinationChainId": DEFAULT_CHAINS[self.dest_chain_var.get()]["chain_id"],
                "originCurrency": NATIVE_TOKEN,
                "destinationCurrency": NATIVE_TOKEN,
                "recipient": recipient,
                "amount": str(int(amount * 10**18)),
                "useDepositAddress": True,
                "refundTo": self.refund_addr_var.get(),
                "tradeType": "EXACT_INPUT"
            }
            
            r = requests.post("https://api.relay.link/quote/v2", json=payload, timeout=10)
            
            if r.status_code == 200:
                data = r.json()
                step = data['steps'][0]
                deposit = step.get('depositAddress', 'N/A')
                req_id = step.get('requestId', 'N/A')[:30]
                
                self.log(f"✅ API 测试成功")
                self.log(f"   中转地址：{deposit[:30]}...")
                self.log(f"   RequestID: {req_id}...")
                
                messagebox.showinfo("成功", f"API 测试成功!\n\n中转地址:\n{deposit[:50]}...")
            else:
                error = r.json().get('message', 'Unknown')
                self.log(f"❌ API 测试失败：{error}")
                messagebox.showerror("失败", f"API 测试失败:\n{error}")
                
        except Exception as e:
            self.log(f"❌ 错误：{e}")
            messagebox.showerror("错误", str(e))
    
    def generate_distribution(self):
        """生成分发计划"""
        if not self.is_connected:
            messagebox.showerror("错误", "请先连接钱包")
            return
        
        wallets_text = self.target_text.get("1.0", tk.END).strip()
        wallets = [w.strip() for w in wallets_text.split('\n') if w.strip().startswith('0x')]
        
        if not wallets:
            messagebox.showerror("错误", "请输入目标钱包地址")
            return
        
        try:
            amount = float(self.pay_single_var.get())
        except:
            messagebox.showerror("错误", "金额无效")
            return
        
        total = amount * len(wallets)
        if total > 1.0:
            if not messagebox.askyesno("警告", f"预计总额 {total:.4f} ETH\n\n是否继续？"):
                return
        
        self.distribution_results = []
        self.progress['maximum'] = len(wallets)
        self.progress['value'] = 0
        
        self.log(f"🚀 开始生成 {self.origin_chain_var.get()} → {self.dest_chain_var.get()} 分发计划")
        self.log(f"📊 共 {len(wallets)} 个钱包")
        
        thread = threading.Thread(target=self._run_distribution, args=(wallets, amount, False))
        thread.daemon = True
        thread.start()
    
    def execute_sending(self):
        """执行实际发送"""
        if not self.is_connected:
            messagebox.showerror("错误", "请先连接钱包")
            return
        
        if not self.distribution_results:
            messagebox.showerror("错误", "请先生成分发计划")
            return
        
        if self.is_sending:
            messagebox.showwarning("警告", "正在发送中，请等待...")
            return
        
        # 预估 Gas 费用和检查余额
        try:
            self.log("🔍 正在检查余额和预估 Gas 费用...")
            origin_chain = self.origin_chain_var.get()
            
            # 获取 Web3 连接
            w3 = self.get_web3_connection(origin_chain)
            
            # 检查余额
            balance = w3.eth.get_balance(self.wallet_address)
            balance_eth = float(w3.from_wei(balance, 'ether'))
            
            # 计算总发送金额
            total_send = sum(r['send_amount'] for r in self.distribution_results)
            
            # 预估 Gas 费用
            first_result = self.distribution_results[0]
            amount_wei = int(first_result['send_amount'] * 10**18)
            
            # 转换为 checksum 地址
            deposit_addr = Web3.to_checksum_address(first_result['deposit_addr'])
            gas_info = self.estimate_gas(w3, self.wallet_address, deposit_addr, amount_wei)
            
            # 计算总 Gas 费用
            total_gas_cost = gas_info['total_cost_eth'] * len(self.distribution_results)
            total_needed = total_send + total_gas_cost
            
            self.log(f"   钱包余额：{balance_eth:.6f} {DEFAULT_CHAINS[origin_chain]['name']}")
            self.log(f"   发送总额：{total_send:.6f} {DEFAULT_CHAINS[origin_chain]['name']}")
            self.log(f"   预估 Gas: {total_gas_cost:.6f} {DEFAULT_CHAINS[origin_chain]['name']}")
            self.log(f"   总计需要：{total_needed:.6f} {DEFAULT_CHAINS[origin_chain]['name']}")
            
            # 检查余额是否充足
            if balance_eth < total_needed:
                error_msg = f"❌ 余额不足!\n\n"
                error_msg += f"当前余额：{balance_eth:.6f} {DEFAULT_CHAINS[origin_chain]['name']}\n"
                error_msg += f"需要总额：{total_needed:.6f} {DEFAULT_CHAINS[origin_chain]['name']}\n\n"
                error_msg += f"缺少：{total_needed - balance_eth:.6f} {DEFAULT_CHAINS[origin_chain]['name']}"
                messagebox.showerror("余额不足", error_msg)
                return
            
            self.log("✅ 余额检查通过!")
            
        except Exception as e:
            self.log(f"❌ 检查失败：{e}")
            messagebox.showerror("错误", f"检查余额和 Gas 失败:\n{e}")
            return
        
        wallet_count = len(self.distribution_results)
        
        msg = f"⚠️ 即将执行实际跨链发送\n\n"
        msg += f"源链：{self.origin_chain_var.get()}\n"
        msg += f"目标链：{self.dest_chain_var.get()}\n"
        msg += f"钱包数量：{wallet_count}\n"
        msg += f"发送总额：{total_send:.6f} {DEFAULT_CHAINS[origin_chain]['name']}\n"
        msg += f"预估 Gas: {total_gas_cost:.6f} {DEFAULT_CHAINS[origin_chain]['name']}\n"
        msg += f"总计需要：{total_needed:.6f} {DEFAULT_CHAINS[origin_chain]['name']}\n\n"
        msg += f"⚠️ 此操作不可撤销，确认继续？"
        
        if not messagebox.askyesno("⚠️ 确认发送", msg):
            return
        
        self.is_sending = True
        self.progress['maximum'] = wallet_count
        self.progress['value'] = 0
        
        self.log("=" * 60)
        self.log("💸 开始执行实际跨链发送...")
        self.log(f"📊 共 {wallet_count} 笔交易")
        
        thread = threading.Thread(target=self._execute_transactions)
        thread.daemon = True
        thread.start()
    
    def _run_distribution(self, wallets, base_amount, execute=False):
        """执行分发计划生成 - 改进错误处理"""
        origin_chain = self.origin_chain_var.get()
        origin_symbol = DEFAULT_CHAINS[origin_chain]["name"]
        dest_chain = self.dest_chain_var.get()
        
        # 检测是否支持 Deposit Address 模式
        use_deposit_address = True
        test_wallet = wallets[0] if wallets else Account.create().address
        
        try:
            test_payload = {
                "user": test_wallet,
                "originChainId": DEFAULT_CHAINS[origin_chain]["chain_id"],
                "destinationChainId": DEFAULT_CHAINS[dest_chain]["chain_id"],
                "originCurrency": NATIVE_TOKEN,
                "destinationCurrency": NATIVE_TOKEN,
                "recipient": test_wallet,
                "amount": "1000000000000000",
                "useDepositAddress": True,
                "refundTo": test_wallet,
                "tradeType": "EXACT_INPUT"
            }
            
            test_r = requests.post("https://api.relay.link/quote/v2", json=test_payload, timeout=10)
            if test_r.status_code != 200:
                error_msg = test_r.json().get('message', '')
                if 'Deposit addresses only supported' in error_msg:
                    use_deposit_address = False
                    self.log("⚠️ 检测到不支持 Deposit Address 模式，使用普通跨链模式")
        except Exception as e:
            self.log(f"⚠️ API 检测失败：{e}")
        
        for i, wallet in enumerate(wallets):
            try:
                random_factor = random.uniform(0.95, 1.05)
                final_amount = base_amount * random_factor
                amount_wei = str(int(final_amount * 10**18))
                
                payload = {
                    "user": wallet,
                    "originChainId": DEFAULT_CHAINS[origin_chain]["chain_id"],
                    "destinationChainId": DEFAULT_CHAINS[dest_chain]["chain_id"],
                    "originCurrency": NATIVE_TOKEN,
                    "destinationCurrency": NATIVE_TOKEN,
                    "recipient": wallet,
                    "amount": amount_wei,
                    "useDepositAddress": use_deposit_address,
                    "refundTo": self.refund_addr_var.get(),
                    "tradeType": "EXACT_INPUT"
                }
                
                r = requests.post("https://api.relay.link/quote/v2", json=payload, timeout=15)
                
                if r.status_code == 200:
                    data = r.json()
                    step = data['steps'][0]
                    
                    # 获取中转地址
                    if use_deposit_address:
                        deposit = step.get('depositAddress', 'N/A')
                    else:
                        # 普通跨链模式从中转地址
                        deposit = step['items'][0]['data'].get('to', 'N/A')
                    
                    req_id = step.get('requestId', 'N/A')
                    
                    result_item = {
                        "index": i+1,
                        "target": wallet,
                        "deposit_addr": deposit,
                        "request_id": req_id,
                        "send_amount": final_amount,
                        "origin_chain": origin_chain,
                        "dest_chain": dest_chain,
                        "use_deposit_address": use_deposit_address
                    }
                    
                    self.distribution_results.append(result_item)
                    
                    self.log(f"✅ [{i+1}/{len(wallets)}] {wallet[:15]}... | {final_amount:.5f} {origin_symbol} | {deposit[:20]}...")
                else:
                    error_data = r.json()
                    error_msg = error_data.get('message', 'Unknown error')
                    self.log(f"❌ [{i+1}/{len(wallets)}] API 错误：{error_msg}")
                
                self.progress['value'] = i + 1
                self.progress_label.config(text=f"进度：{i+1}/{len(wallets)}")
                
            except Exception as e:
                self.log(f"❌ [{i+1}/{len(wallets)}] 失败：{str(e)[:100]}")
                self.progress['value'] = i + 1
        
        self.log(f"\n✨ 完成！成功 {len(self.distribution_results)}/{len(wallets)} 个")
        self.progress_label.config(text=f"✅ 完成 - 成功 {len(self.distribution_results)} 个")
        
        if self.distribution_results:
            messagebox.showinfo("成功", f"✅ 成功生成 {len(self.distribution_results)} 个分发计划!\n\n点击\"💸 执行发送\"开始实际跨链交易")
    
    def _execute_transactions(self):
        """执行实际的交易发送"""
        success_count = 0
        failed_count = 0
        
        for i, result in enumerate(self.distribution_results):
            try:
                self.log(f"\n{'='*60}")
                self.log(f"💸 [{i+1}/{len(self.distribution_results)}] 发送到 {result['target'][:15]}...")
                
                origin_chain = result['origin_chain']
                deposit_addr = result['deposit_addr']
                amount_eth = result['send_amount']
                amount_wei = int(amount_eth * 10**18)
                
                # 转换为 checksum 地址
                deposit_checksum = Web3.to_checksum_address(deposit_addr)
                self.log(f"   中转地址：{deposit_checksum}")
                
                tx_result = self.send_transaction(
                    chain_name=origin_chain,
                    to_address=deposit_checksum,
                    amount_wei=amount_wei
                )
                
                if tx_result['success']:
                    result['tx_hash'] = tx_result['tx_hash']
                    result['gas_used'] = tx_result['gas_used']
                    result['block_number'] = tx_result['block_number']
                    result['explorer_url'] = tx_result['explorer_url']
                    result['status'] = 'success'
                    
                    success_count += 1
                    self.log(f"✅ 交易成功!")
                    self.log(f"   TxHash: {tx_result['tx_hash']}")
                    self.log(f"   Gas: {tx_result['gas_used']}")
                    self.log(f"   区块：{tx_result['block_number']}")
                else:
                    result['status'] = 'failed'
                    result['error'] = tx_result.get('error', 'Unknown error')
                    
                    failed_count += 1
                    self.log(f"❌ 交易失败：{result['error']}")
                
                self.progress['value'] = i + 1
                self.progress_label.config(text=f"进度：{i+1}/{len(self.distribution_results)} | 成功：{success_count} | 失败：{failed_count}")
                
                delay = random.uniform(3, 8)
                self.log(f"⏳ 等待 {delay:.1f} 秒...")
                time.sleep(delay)
                
            except Exception as e:
                failed_count += 1
                self.log(f"❌ 发送异常：{str(e)[:100]}")
                result['status'] = 'error'
                result['error'] = str(e)
                
                self.progress['value'] = i + 1
        
        self.log("\n" + "="*60)
        self.log(f"🎉 发送完成!")
        self.log(f"✅ 成功：{success_count}")
        self.log(f"❌ 失败：{failed_count}")
        self.log("="*60)
        
        self.progress_label.config(text=f"✅ 发送完成 | 成功：{success_count} | 失败：{failed_count}")
        self.is_sending = False
        
        messagebox.showinfo("发送完成", 
                          f"🎉 跨链发送完成!\n\n"
                          f"✅ 成功：{success_count}\n"
                          f"❌ 失败：{failed_count}\n\n"
                          f"点击\"💾 导出结果\"保存交易记录")
    
    def export_results(self):
        """导出结果"""
        if not self.distribution_results:
            messagebox.showwarning("警告", "没有可导出的结果")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".json", 
                                                  filetypes=[("JSON 文件", "*.json")])
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.distribution_results, f, indent=2, ensure_ascii=False)
            
            self.log(f"💾 结果已导出：{file_path}")
            messagebox.showinfo("成功", f"已导出 {len(self.distribution_results)} 条记录")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{e}")


def main():
    root = tk.Tk()
    app = CrossChainDistributor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
