# 🔗 Relay Cross-Chain Distributor - CLI Version

**命令行版跨链转账工具** - 轻量级命令行界面，适合脚本和自动化

## ✨ 功能特性

- ✅ **轻量级** - 无需 GUI，纯命令行
- ✅ **自动化** - 适合脚本和批量处理
- ✅ **80+ 链支持** - ETH、Base、BSC、Arbitrum 等
- ✅ **批量发送** - 从文件加载钱包地址
- ✅ **JSON 输出** - 结构化结果，便于解析
- ✅ **可编程** - 易于集成到其他系统

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备钱包列表

创建 `wallets.txt` 文件：
```
0x2159864c15A8C0Bb74F3E9f57a4bfbAF5C46135b
0xb8eB8fc92143A590351356Ed8F64731660DA1606
0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

### 3. 生成分发计划

```bash
python cli.py \
  --private-key YOUR_PRIVATE_KEY \
  --origin-chain Ethereum \
  --dest-chain BSC \
  --amount 0.001 \
  --wallets-file wallets.txt \
  --output plan.json
```

### 4. 执行发送

```bash
python cli.py \
  --private-key YOUR_PRIVATE_KEY \
  --origin-chain Ethereum \
  --dest-chain BSC \
  --amount 0.001 \
  --wallets-file wallets.txt \
  --output result.json \
  --execute
```

## 📋 命令参数

### 必需参数

- `--private-key` - 钱包私钥
- `--amount` - 每个钱包发送的金额（ETH）
- `--wallets-file` - 钱包地址文件路径

### 可选参数

- `--origin-chain` - 源链（默认：Ethereum）
- `--dest-chain` - 目标链（默认：BSC）
- `--output` - 输出文件（默认：result.json）
- `--execute` - 执行实际发送（不加此参数仅生成计划）

## 🛠️ 使用示例

### 示例 1: 检查余额

```bash
python cli.py \
  --private-key 0x... \
  --origin-chain Ethereum \
  --amount 0.001 \
  --wallets-file wallets.txt
```

输出：
```
Wallet: 0x50ECccDD83eEB38d5224813B2DDEA6D0f7A82235
Balance: 0.008444 ETH on Ethereum

Loaded 2 wallets from wallets.txt
Generating distribution plan for 2 wallets...
✅ [1/2] 0x2159864c15A8C0Bb...
✅ [2/2] 0xb8eB8fc92143A59035...
✨ Generated 2/2 plans

💾 Results saved to result.json
```

### 示例 2: Base → BSC

```bash
python cli.py \
  --private-key 0x... \
  --origin-chain Base \
  --dest-chain BSC \
  --amount 0.0005 \
  --wallets-file wallets.txt \
  --output base_to_bsc.json \
  --execute
```

### 示例 3: Arbitrum → BSC

```bash
python cli.py \
  --private-key 0x... \
  --origin-chain Arbitrum \
  --dest-chain BSC \
  --amount 0.001 \
  --wallets-file wallets.txt \
  --execute
```

## 📊 输出格式

### JSON 结果示例

```json
{
  "wallet": "0x50ECccDD83eEB38d5224813B2DDEA6D0f7A82235",
  "origin_chain": "Ethereum",
  "dest_chain": "BSC",
  "transactions": [
    {
      "index": 1,
      "target": "0x2159864c15A8C0Bb74F3E9f57a4bfbAF5C46135b",
      "deposit_address": "0x4cd00e387622c35bddb9b4c962c136462338bc31",
      "send_amount": 0.001,
      "tx_hash": "0xde911997ada738004053e39114112949ccab68b8b014453e4037f1ff6db002e5",
      "status": "success",
      "block_number": 24602607,
      "gas_used": 24824,
      "actual_gas_eth": 0.000000908,
      "explorer_url": "https://etherscan.io/tx/0xde911997ada738004053e39114112949ccab68b8b014453e4037f1ff6db002e5"
    }
  ]
}
```

## 💡 高级用法

### 集成到脚本

```bash
#!/bin/bash
# Batch cross-chain distribution

PRIVATE_KEY="0x..."
AMOUNT="0.001"
WALLETS="wallets.txt"

# Ethereum → BSC
python cli.py --private-key $PRIVATE_KEY --origin-chain Ethereum --dest-chain BSC --amount $AMOUNT --wallets-file $WALLETS --execute

# Wait 60 seconds
sleep 60

# Base → BSC
python cli.py --private-key $PRIVATE_KEY --origin-chain Base --dest-chain BSC --amount $AMOUNT --wallets-file $WALLETS --execute
```

### Python 集成

```python
import subprocess
import json

def run_distribution(private_key, origin, dest, amount, wallets_file):
    cmd = [
        'python', 'cli.py',
        '--private-key', private_key,
        '--origin-chain', origin,
        '--dest-chain', dest,
        '--amount', str(amount),
        '--wallets-file', wallets_file,
        '--output', 'result.json',
        '--execute'
    ]
    
    subprocess.run(cmd)
    
    with open('result.json') as f:
        return json.load(f)

# Usage
result = run_distribution(
    private_key='0x...',
    origin='Ethereum',
    dest='BSC',
    amount=0.001,
    wallets_file='wallets.txt'
)

print(f"Success: {sum(1 for tx in result['transactions'] if tx['status'] == 'success')}")
```

## ⚠️ 安全提示

### 重要提醒

- ⚠️ **私钥仅存储在内存**
- ⚠️ **不要在命令历史中保存私钥**
- ⚠️ **使用环境变量或配置文件**
- ⚠️ **小额测试后再大额**

### 使用环境变量

```bash
# 设置环境变量
export PRIVATE_KEY="0x..."

# 使用环境变量
python cli.py \
  --private-key $PRIVATE_KEY \
  --origin-chain Ethereum \
  --dest-chain BSC \
  --amount 0.001 \
  --wallets-file wallets.txt \
  --execute
```

## 🛠️ 支持的链

| 链 | Chain ID | 浏览器 |
|---|---|---|
| Ethereum | 1 | [etherscan.io](https://etherscan.io) |
| Base | 8453 | [basescan.org](https://basescan.org) |
| BSC | 56 | [bscscan.com](https://bscscan.com) |
| Arbitrum | 42161 | [arbiscan.io](https://arbiscan.io) |
| Optimism | 10 | [optimistic.etherscan.io](https://optimistic.etherscan.io) |
| Polygon | 137 | [polygonscan.com](https://polygonscan.com) |
| Avalanche | 43114 | [snowtrace.io](https://snowtrace.io) |

## 🐛 故障排除

### 找不到模块

**错误**: `ModuleNotFoundError: No module named 'web3'`

**解决**:
```bash
pip install -r requirements.txt
```

### 私钥格式错误

**错误**: "Private key invalid"

**解决**:
- 确保私钥带或不带 0x 均可
- 检查私钥长度（64 或 66 字符）

### 连接失败

**错误**: "Cannot connect to Ethereum"

**解决**:
- 检查网络连接
- 尝试切换网络或使用 VPN

## 🔗 相关链接

- [GitHub 仓库](https://github.com/LegionZYX/relay-cross-chain-distributor)
- [Relay API 文档](https://docs.relay.link/)
- [Etherscan](https://etherscan.io/)

---

**适合自动化和脚本使用！** 🚀

**⚠️ 首次使用请务必小额测试！**
