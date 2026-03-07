# 🔗 Relay Cross-Chain Distributor

**批量跨链转账工具** - 使用 Relay API 实现从 ETH 主网到其他链的批量跨链转账

## ✨ 功能特性

- ✅ **支持 80+ 条链** - ETH、Base、BSC、Arbitrum、Optimism 等
- ✅ **批量发送** - 一次操作可发送到数十个钱包
- ✅ **实时 Gas 预估** - 发送前显示预估 Gas 费用
- ✅ **余额检查** - 自动检查余额是否充足
- ✅ **交易记录** - 完整保存所有交易哈希和详情
- ✅ **GUI 界面** - 简洁易用的图形界面
- ✅ **自动确认** - 等待交易确认并显示进度

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行程序

**命令行方式:**
```bash
python main.py
```

**Windows 用户:** 双击 `启动-v2.bat`

### 3. 使用步骤

1. **导入私钥** - 点击 "🔑 私钥导入" 输入私钥
2. **配置跨链参数**
   - 源链：选择 Ethereum
   - 目标链：选择 BSC 或其他链
   - 支付 Token：选择 Native (ETH)
   - 接收 Token：选择目标链原生 Token
3. **设置金额和数量**
   - 单个金额：每个钱包发送的金额
   - 钱包数量：目标钱包数量
4. **加载目标钱包**
   - 手动输入地址（每行一个）
   - 或点击 "📂 加载文件" 导入 txt/json 文件
5. **生成分发计划** - 点击 "🚀 生成分发计划"
6. **执行发送** - 点击 "💸 执行发送" 确认并发送
7. **导出结果** - 点击 "💾 导出结果" 保存交易记录

## 📋 示例文件

### 钱包列表格式 (wallets.txt)

```
0x2159864c15A8C0Bb74F3E9f57a4bfbAF5C46135b
0xb8eB8fc92143A590351356Ed8F64731660DA1606
0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb
```

### 导出结果示例 (result.json)

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

## 🔧 配置说明

### 支持的链

| 链 | Chain ID | RPC | 浏览器 |
|---|---|---|---|
| Ethereum | 1 | eth.llamarpc.com | etherscan.io |
| Base | 8453 | mainnet.base.org | basescan.org |
| BSC | 56 | bsc-dataseed.binance.org | bscscan.com |
| Arbitrum | 42161 | arb1.arbitrum.io/rpc | arbiscan.io |
| Optimism | 10 | mainnet.optimism.io | optimistic.etherscan.io |
| Polygon | 137 | polygon-rpc.com | polygonscan.com |
| Avalanche | 43114 | api.avax.network | snowtrace.io |

### 跨链路径示例

- ✅ **Ethereum → BSC** - ETH 跨链到 BSC 换取 BNB
- ✅ **Ethereum → Base** - ETH 跨链到 Base
- ✅ **Base → BSC** - Base 上的 ETH 跨链到 BSC
- ✅ **Arbitrum → BSC** - Arbitrum 上的 ETH 跨链到 BSC

## ⚠️ 重要提示

### 首次使用必读

1. **小额测试**
   - 首次使用建议发送 0.0005-0.001 ETH 测试
   - 确认流程正确后再进行大额操作

2. **余额充足**
   - 确保源钱包有足够余额（发送金额 + Gas 费用）
   - Gas 费用预估会显示在确认对话框中

3. **网络选择**
   - 建议使用低 Gas 链（Base、Arbitrum）
   - 避开网络高峰期

4. **私钥安全**
   - 私钥仅存储在内存中
   - 程序关闭后自动清除
   - 不会上传到任何服务器

### 费用说明

- **发送金额**: 您设置的跨链金额
- **Gas 费用**: ETH 主网交易手续费（约 0.000001-0.00001 ETH）
- **跨链手续费**: Relay 收取约 0.5% 手续费（自动扣除）

## 🛠️ 命令行工具

### 测试依赖

```bash
python test-dependencies.py
```

### 验证安装

```bash
python verify-update.py
```

## 📊 交易查询

交易完成后，可以通过以下方式查询：

1. **ETH 主网交易**: [Etherscan](https://etherscan.io/tx/YOUR_TX_HASH)
2. **BSC 到账**: [BSCScan](https://bscscan.com/address/YOUR_WALLET)
3. **Base 到账**: [BaseScan](https://basescan.org/address/YOUR_WALLET)

## 🐛 故障排除

### 问题 1: 余额不足

**错误**: "余额不足，需要至少 X ETH"

**解决**: 
- 检查钱包余额
- 充值到源钱包地址
- 预留 Gas 费用（约 5-10%）

### 问题 2: API 错误

**错误**: "API 错误：Deposit addresses only supported"

**解决**:
- 某些链组合不支持 Deposit Address 模式
- 程序会自动切换到普通跨链模式
- 或更换其他链组合

### 问题 3: 交易失败

**错误**: "交易失败" 或 "Transaction reverted"

**解决**:
- 检查 Gas 费用是否充足
- 检查目标地址格式是否正确
- 在区块链浏览器查看失败原因

### 问题 4: 连接超时

**错误**: "无法连接到 RPC 节点"

**解决**:
- 检查网络连接
- 尝试切换网络或使用 VPN
- 等待几分钟后重试

## 📝 更新日志

### v2.0.0 (2026-03-07)

**新增功能:**
- ✅ 实际交易发送功能
- ✅ Gas 预估和余额检查
- ✅ EIP-1559 交易支持
- ✅ 详细确认对话框
- ✅ 交易记录导出

**修复:**
- 🔧 按钮样式问题
- 🔧 Web3 版本兼容性
- 🔧 编码问题（Windows）

## 📄 许可证

MIT License

## 💬 技术支持

遇到问题？

1. 查看程序内日志
2. 检查导出的 JSON 结果文件
3. 在区块链浏览器查询交易状态

## 🔗 相关链接

- [Relay API 文档](https://docs.relay.link/)
- [Etherscan](https://etherscan.io/)
- [BSCScan](https://bscscan.com/)
- [BaseScan](https://basescan.org/)

---

**享受无缝的跨链体验！** 🚀

**⚠️ 重要提醒**: 首次使用请务必小额测试！
