#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Relay Cross-Chain Distributor - CLI Version
Command Line Interface for batch cross-chain transfers
"""

import sys
import json
import time
import argparse
from web3 import Web3
from eth_account import Account
import requests

# Chain configuration
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

class CrossChainDistributor:
    def __init__(self, private_key):
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
        
        self.account = Account.from_key(private_key)
        self.address = self.account.address
        self.private_key = private_key
    
    def log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def get_balance(self, chain):
        """Get wallet balance"""
        rpc = CHAINS[chain]['rpc']
        w3 = Web3(Web3.HTTPProvider(rpc))
        
        if not w3.is_connected():
            raise Exception(f"Cannot connect to {chain}")
        
        balance_wei = w3.eth.get_balance(self.address)
        return float(w3.from_wei(balance_wei, 'ether'))
    
    def get_quote(self, origin_chain, dest_chain, amount, recipient):
        """Get cross-chain quote"""
        payload = {
            "user": recipient,
            "originChainId": CHAINS[origin_chain]["chain_id"],
            "destinationChainId": CHAINS[dest_chain]["chain_id"],
            "originCurrency": NATIVE_TOKEN,
            "destinationCurrency": NATIVE_TOKEN,
            "recipient": recipient,
            "amount": str(int(float(amount) * 10**18)),
            "useDepositAddress": False,
            "refundTo": self.address,
            "tradeType": "EXACT_INPUT"
        }
        
        response = requests.post(RELAY_API, json=payload, timeout=15)
        
        if response.status_code != 200:
            raise Exception(f"API error: {response.json().get('message', 'Unknown')}")
        
        data = response.json()
        step = data['steps'][0]
        tx_data = step['items'][0]['data']
        
        return {
            'deposit_address': tx_data['to'],
            'value': tx_data['value'],
            'data': tx_data['data'],
            'gas': int(tx_data.get('gas', 200000)),
            'maxFeePerGas': int(tx_data.get('maxFeePerGas', 0)),
            'maxPriorityFeePerGas': int(tx_data.get('maxPriorityFeePerGas', 0))
        }
    
    def generate_distribution(self, wallets, amount, origin_chain, dest_chain):
        """Generate distribution plan"""
        results = []
        
        self.log(f"Generating distribution plan for {len(wallets)} wallets...")
        
        for i, wallet in enumerate(wallets):
            if not wallet.startswith('0x'):
                continue
            
            try:
                quote = self.get_quote(origin_chain, dest_chain, amount, wallet)
                
                results.append({
                    'index': i + 1,
                    'target': wallet,
                    'deposit_address': quote['deposit_address'],
                    'value': quote['value'],
                    'data': quote['data'],
                    'gas': quote['gas'],
                    'maxFeePerGas': quote['maxFeePerGas'],
                    'maxPriorityFeePerGas': quote['maxPriorityFeePerGas'],
                    'send_amount': amount,
                    'origin_chain': origin_chain,
                    'dest_chain': dest_chain
                })
                
                self.log(f"✅ [{i+1}/{len(wallets)}] {wallet[:20]}...")
            except Exception as e:
                self.log(f"❌ [{i+1}/{len(wallets)}] Failed: {e}")
        
        self.log(f"✨ Generated {len(results)}/{len(wallets)} plans")
        return results
    
    def execute_transaction(self, result):
        """Execute single transaction"""
        try:
            rpc = CHAINS[result['origin_chain']]['rpc']
            w3 = Web3(Web3.HTTPProvider(rpc))
            
            nonce = w3.eth.get_transaction_count(self.address)
            
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
            
            signed_tx = w3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            tx_hash_hex = w3.to_hex(tx_hash)
            
            self.log(f"📤 Sent: {tx_hash_hex[:30]}...")
            
            # Wait for confirmation
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
                
                self.log(f"✅ Success! Gas: {actual_gas_eth:.6f} ETH")
                return True
            else:
                result['status'] = 'failed'
                result['tx_hash'] = tx_hash_hex
                self.log(f"❌ Failed")
                return False
                
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            self.log(f"❌ Error: {e}")
            return False
    
    def execute_distribution(self, results):
        """Execute all transactions"""
        self.log("=" * 60)
        self.log("💸 Starting cross-chain transfers...")
        
        success_count = 0
        failed_count = 0
        
        for i, result in enumerate(results):
            self.log(f"\n[{i+1}/{len(results)}] Sending to {result['target'][:20]}...")
            
            if self.execute_transaction(result):
                success_count += 1
            else:
                failed_count += 1
            
            if i < len(results) - 1:
                self.log("Waiting 10 seconds...")
                time.sleep(10)
        
        self.log("=" * 60)
        self.log(f"🎉 Completed! Success: {success_count} | Failed: {failed_count}")
        
        return results

def load_wallets(filepath):
    """Load wallets from file"""
    wallets = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('0x'):
                wallets.append(line)
    return wallets

def main():
    parser = argparse.ArgumentParser(description='Relay Cross-Chain Distributor CLI')
    parser.add_argument('--private-key', required=True, help='Wallet private key')
    parser.add_argument('--origin-chain', default='Ethereum', help='Origin chain')
    parser.add_argument('--dest-chain', default='BSC', help='Destination chain')
    parser.add_argument('--amount', type=float, required=True, help='Amount per wallet (ETH)')
    parser.add_argument('--wallets-file', required=True, help='File with wallet addresses')
    parser.add_argument('--output', default='result.json', help='Output file')
    parser.add_argument('--execute', action='store_true', help='Execute transfers')
    
    args = parser.parse_args()
    
    # Initialize distributor
    distributor = CrossChainDistributor(args.private_key)
    
    print("=" * 60)
    print("  Relay Cross-Chain Distributor - CLI")
    print("=" * 60)
    print(f"\nWallet: {distributor.address}")
    
    # Check balance
    balance = distributor.get_balance(args.origin_chain)
    print(f"Balance: {balance:.6f} ETH on {args.origin_chain}")
    
    # Load wallets
    wallets = load_wallets(args.wallets_file)
    print(f"\nLoaded {len(wallets)} wallets from {args.wallets_file}")
    
    # Generate distribution
    results = distributor.generate_distribution(
        wallets, 
        args.amount, 
        args.origin_chain, 
        args.dest_chain
    )
    
    # Execute if requested
    if args.execute:
        print("\n⚠️  WARNING: This will execute REAL transactions!")
        confirm = input("Type 'yes' to confirm: ")
        
        if confirm.lower() == 'yes':
            results = distributor.execute_distribution(results)
        else:
            print("Cancelled")
    
    # Save results
    with open(args.output, 'w') as f:
        json.dump({
            'wallet': distributor.address,
            'origin_chain': args.origin_chain,
            'dest_chain': args.dest_chain,
            'transactions': results
        }, f, indent=2)
    
    print(f"\n💾 Results saved to {args.output}")

if __name__ == '__main__':
    main()
