# 🔗 Relay Cross-Chain Distributor

**批量跨链转账工具** - 使用 Relay API 实现从 ETH 主网到其他链的批量跨链转账

## ✨ 功能特性

- ✅ 支持 80+ 条链 - ETH、Base、BSC、Arbitrum、Optimism 等
- ✅ 批量发送 - 一次操作可发送到数十个钱包
- ✅ 实时 Gas 预估 - 发送前显示预估 Gas 费用
- ✅ 余额检查 - 自动检查余额是否充足
- ✅ 交易记录 - 完整保存所有交易哈希和详情
- ✅ GUI 界面 - 简洁易用的图形界面

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行程序

```bash
python main.py
```

### 3. 使用步骤

1. **导入私钥** - 点击 "🔑 私钥导入"
2. **配置跨链** - 源链：Ethereum，目标链：BSC
3. **设置金额** - 建议测试：0.0005 ETH
4. **加载钱包** - 输入目标钱包地址（每行一个）
5. **生成计划** - 点击 "🚀 生成分发计划"
6. **执行发送** - 点击 "💸 执行发送"
7. **导出结果** - 保存交易记录

## 📋 示例钱包文件 (wallets.txt)

```
0x2159864c15A8C0Bb74F3E9f57a4bfbAF5C46135b
0xb8eB8fc92143A590351356Ed8F64731660DA1606
0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

## 🛠️ 支持的链

| 链 | Chain ID | 浏览器 |
|---|---|---|
| Ethereum | 1 | etherscan.io |
| Base | 8453 | basescan.org |
| BSC | 56 | bscscan.com |
| Arbitrum | 42161 | arbiscan.io |
| Optimism | 10 | optimistic.etherscan.io |
| Polygon | 137 | polygonscan.com |
| Avalanche | 43114 | snowtrace.io |

## ⚠️ 重要提示

### 首次使用必读

1. **小额测试** - 建议 0.0005-0.001 ETH
2. **余额充足** - 预留 Gas 费用（约 10%）
3. **验证流程** - 确认无误后大额操作

### 安全警告

- ⚠️ 私钥仅存储在内存，程序关闭自动清除
- ⚠️ 不要在公共网络使用
- ⚠️ 交易不可逆转
- ⚠️ 自行承担风险

## 💡 使用技巧

### 节省 Gas

- 选择低峰期：UTC 00:00-10:00
- 使用低 Gas 链：Base、Arbitrum
- 批量发送：一次性发送多个

### 交易时间

- ETH 确认：1-3 分钟
- 跨链桥接：2-5 分钟
- 目标链到账：1-2 分钟
- **总计：5-10 分钟**

## 📊 交易记录

导出结果示例：

```json
{
  "timestamp": "2026-03-07 10:31:55",
  "from_wallet": "0x50ECccDD83eEB38d5224813B2DDEA6D0f7A82235",
  "origin_chain": "Ethereum",
  "destination_chain": "BSC",
  "transactions": [
    {
      "wallet_index": 1,
      "recipient": "0x2159864c15A8C0Bb74F3E9f57a4bfbAF5C46135b",
      "status": "success",
      "tx_hash": "0xde911997ada738004053e39114112949ccab68b8b014453e4037f1ff6db002e5",
      "block_number": 24602607,
      "gas_used": 24824,
      "actual_gas_eth": 0.000000908,
      "explorer_url": "https://etherscan.io/tx/0xde911997ada738004053e39114112949ccab68b8b014453e4037f1ff6db002e5"
    }
  ]
}
```

## 🐛 故障排除

### 余额不足

**错误**: "余额不足，需要至少 X ETH"

**解决**: 
- 检查钱包余额
- 充值到源钱包地址
- 预留 Gas 费用

### API 错误

**错误**: "API 错误：Deposit addresses only supported"

**解决**:
- 某些链组合不支持 Deposit Address 模式
- 程序会自动切换模式
- 或更换其他链组合

### 交易失败

**错误**: "交易失败"

**解决**:
- 检查 Gas 费用是否充足
- 检查目标地址格式
- 在区块链浏览器查看原因

## 🔗 相关链接

- [Relay API 文档](https://docs.relay.link/)
- [Etherscan](https://etherscan.io/)
- [BSCScan](https://bscscan.com/)
- [BaseScan](https://basescan.org/)

---

**享受无缝的跨链体验！** 🚀

**⚠️ 重要提醒**: 首次使用请务必小额测试！
