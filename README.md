# 🔗 Relay Cross-Chain Distributor v2.0

**批量跨链转账工具** - 使用 Relay API 实现从 ETH 主网到其他链的批量跨链转账

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ 功能特性

- ✅ **80+ 链支持** - ETH、Base、BSC、Arbitrum、Optimism 等
- ✅ **批量发送** - 一次操作可发送到数十个钱包
- ✅ **Gas 预估** - 发送前显示预估 Gas 费用
- ✅ **余额检查** - 自动检查余额是否充足
- ✅ **交易记录** - 完整保存所有交易哈希
- ✅ **GUI 界面** - 简洁易用的图形界面

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/LegionZYX/relay-cross-chain-distributor.git
cd relay-cross-chain-distributor
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 运行程序

```bash
python main.py
```

## 📋 使用步骤

1. **导入私钥** - 点击 "🔑 私钥导入"
2. **配置跨链** - 源链：Ethereum，目标链：BSC
3. **设置金额** - 建议测试：0.0005 ETH
4. **加载钱包** - 输入目标钱包地址
5. **生成计划** - 点击 "🚀 生成分发计划"
6. **执行发送** - 点击 "💸 执行发送"
7. **导出结果** - 保存交易记录

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

## 📊 测试结果

**ETH → BSC 跨链测试成功！**

- ✅ 2 笔交易全部成功
- ✅ Gas 费用：~0.000001 ETH/笔
- ✅ 确认时间：< 30 秒

## ⚠️ 重要提示

### 首次使用

1. **小额测试** - 建议 0.0005-0.001 ETH
2. **余额充足** - 预留 Gas 费用（约 10%）
3. **验证流程** - 确认后再大额操作

### 安全警告

- ⚠️ 私钥仅存储在内存，程序关闭自动清除
- ⚠️ 不要在公共网络使用
- ⚠️ 交易不可逆转
- ⚠️ 自行承担风险

## 📚 文档

- [QUICKSTART.md](QUICKSTART.md) - 3 分钟快速上手
- [RELEASE.md](RELEASE.md) - 发布说明和更新日志
- [CLEANUP.md](CLEANUP.md) - 清理说明

## 🔗 相关链接

- [Relay API 文档](https://docs.relay.link/)
- [Etherscan](https://etherscan.io/)
- [BSCScan](https://bscscan.com/)

---

**享受无缝的跨链体验！** 🚀

**⚠️ 首次使用请务必小额测试！**
