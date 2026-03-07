# 🔗 Relay Cross-Chain Distributor

**批量跨链转账工具** - 使用 Relay API 实现多链之间的批量跨链转账

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## 📦 版本选择

本项目提供**三个版本**，满足不同使用场景：

### 🖥️ GUI 桌面版（推荐新手）

**特点:**
- ✅ 图形界面，简单易用
- ✅ 本地运行，最安全
- ✅ 实时日志和进度显示

**适合:**
- 👤 个人使用
- 🎯 注重安全性
- 🚀 快速上手

**[👉 查看桌面版](#-gui-桌面版)**

---

### 🌐 Web 网页版（团队协作）

**特点:**
- ✅ 美观的 Web 界面
- ✅ 可通过浏览器访问
- ✅ 支持云端部署

**适合:**
- 👥 团队协作
- 🌍 远程访问
- ☁️ 云端部署

**[👉 查看网页版](#-web-网页版)**

---

### 💻 CLI 命令行版（自动化）

**特点:**
- ✅ 轻量级命令行
- ✅ 适合脚本自动化
- ✅ 可编程集成

**适合:**
- 🤖 自动化脚本
- 🔧 系统集成
- ⚙️ 高级用户

**[👉 查看命令行版](#-cli-命令行版)**

---

## 🤔 如何选择？

### 快速决策树

```
你需要什么？
│
├─ 简单易用、个人使用
│  └─ 选择 GUI 桌面版 ✅
│
├─ 团队协作、远程访问
│  └─ 选择 Web 网页版 ✅
│
└─ 自动化、脚本集成
   └─ 选择 CLI 命令行版 ✅
```

### 详细对比

| 特性 | GUI 桌面版 | Web 网页版 | CLI 命令行版 |
|---|---|---|---|
| **界面** | Tkinter GUI | HTML/CSS/JS | 命令行 |
| **易用性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **安全性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **美观度** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **可部署** | ❌ | ✅ | ❌ |
| **自动化** | ❌ | ❌ | ✅ |
| **团队协作** | ❌ | ✅ | ✅ |
| **远程访问** | ❌ | ✅ | ❌ |
| **系统要求** | 桌面环境 | Python + 浏览器 | Python |

---

## 🖥️ GUI 桌面版

### 快速开始

```bash
# 1. 克隆仓库
git clone https://github.com/LegionZYX/relay-cross-chain-distributor.git
cd relay-cross-chain-distributor

# 2. 切换分支
git checkout main

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行程序
python main.py
```

### 使用步骤

1. **导入私钥** - 点击 "🔑 私钥导入"
2. **配置跨链** - 源链：Ethereum，目标链：BSC
3. **设置金额** - 建议：0.0005 ETH（测试）
4. **加载钱包** - 输入或导入目标钱包地址
5. **生成计划** - 点击 "🚀 生成分发计划"
6. **执行发送** - 点击 "💸 执行发送"
7. **导出结果** - 保存交易记录

### 功能特性

- ✅ 80+ 链支持
- ✅ 批量发送
- ✅ Gas 预估
- ✅ 余额检查
- ✅ 实时日志
- ✅ 交易记录

**[📖 查看完整文档](#)**

---

## 🌐 Web 网页版

### 快速开始

```bash
# 1. 切换分支
git checkout web-version

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动服务
python app.py

# 4. 访问浏览器
# http://localhost:5000
```

### 部署到云端

**Railway**:
1. 访问 https://railway.app
2. 连接 GitHub 仓库
3. 选择 `web-version` 分支
4. 自动部署

**Render**:
1. 访问 https://render.com
2. 创建 Web Service
3. 选择 `web-version` 分支
4. 配置启动命令：`python app.py`

### 功能特性

- ✅ 美观的响应式界面
- ✅ 实时日志和进度
- ✅ 可远程访问
- ✅ 支持团队协作
- ✅ 云端部署

**[📖 查看完整文档](#)**

---

## 💻 CLI 命令行版

### 快速开始

```bash
# 1. 切换分支
git checkout cli-version

# 2. 安装依赖
pip install -r requirements.txt

# 3. 准备钱包列表
# 创建 wallets.txt 文件，每行一个地址

# 4. 生成分发计划
python cli.py \
  --private-key YOUR_PRIVATE_KEY \
  --origin-chain Ethereum \
  --dest-chain BSC \
  --amount 0.001 \
  --wallets-file wallets.txt

# 5. 执行发送
python cli.py \
  --private-key YOUR_PRIVATE_KEY \
  --origin-chain Ethereum \
  --dest-chain BSC \
  --amount 0.001 \
  --wallets-file wallets.txt \
  --execute
```

### 命令参数

- `--private-key` - 钱包私钥
- `--origin-chain` - 源链（默认：Ethereum）
- `--dest-chain` - 目标链（默认：BSC）
- `--amount` - 金额（ETH）
- `--wallets-file` - 钱包地址文件
- `--output` - 输出文件（默认：result.json）
- `--execute` - 执行实际发送

### 自动化示例

```bash
#!/bin/bash
# 批量跨链脚本

for chain in Base Arbitrum Optimism; do
  python cli.py \
    --private-key $PRIVATE_KEY \
    --origin-chain $chain \
    --dest-chain BSC \
    --amount 0.001 \
    --wallets-file wallets.txt \
    --execute
  
  sleep 60
done
```

**[📖 查看完整文档](#)**

---

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

---

## ⚠️ 安全提示

### 重要提醒

- ⚠️ **私钥仅存储在内存**
- ⚠️ **程序关闭自动清除**
- ⚠️ **交易不可逆转**
- ⚠️ **自行承担风险**

### 最佳实践

1. **小额测试** - 首次使用 0.0005-0.001 ETH
2. **专用钱包** - 不要使用主钱包
3. **余额预留** - 预留 10% Gas 费用
4. **验证地址** - 确认所有地址正确
5. **备份记录** - 定期导出交易记录

---

## 📊 测试结果

**ETH → BSC 跨链测试成功！**

- ✅ 2 笔交易全部成功
- ✅ Gas 费用：~0.000001 ETH/笔
- ✅ 确认时间：< 30 秒

**交易哈希:**
- [0xde911997ada738004053e39114112949ccab68b8b014453e4037f1ff6db002e5](https://etherscan.io/tx/0xde911997ada738004053e39114112949ccab68b8b014453e4037f1ff6db002e5)
- [0x7ec93e3fd9018898f4c336b84220f70631cd8d0d5551368af53871fab309b00d](https://etherscan.io/tx/0x7ec93e3fd9018898f4c336b84220f70631cd8d0d5551368af53871fab309b00d)

---

## 🐛 故障排除

### 余额不足

**解决**: 
- 检查钱包余额
- 预留 Gas 费用（10%）

### API 错误

**解决**:
- 检查网络连接
- 更换链组合

### 交易失败

**解决**:
- 查看 Etherscan 详情
- 检查 Gas 费用

---

## 🔗 相关链接

- [Relay API 文档](https://docs.relay.link/)
- [Etherscan](https://etherscan.io/)
- [BSCScan](https://bscscan.com/)
- [BaseScan](https://basescan.org/)

---

## 📞 技术支持

遇到问题？

1. 查看执行日志
2. 检查交易记录
3. 在区块链浏览器查询
4. 提交 GitHub Issue

---

## 📄 许可证

MIT License

---

**选择适合你的版本，开始跨链之旅！** 🚀

**⚠️ 重要提醒: 首次使用请务必小额测试！**
