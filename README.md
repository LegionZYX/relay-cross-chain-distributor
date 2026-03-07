# 🔗 Relay Cross-Chain Distributor - Web Version

**网页版跨链转账工具** - 使用浏览器即可进行跨链转账，无需安装 Python 环境！

## ✨ 功能特性

- ✅ **网页界面** - 美观易用的 Web UI
- ✅ **80+ 链支持** - ETH、Base、BSC、Arbitrum 等
- ✅ **批量发送** - 一次操作可发送到数十个钱包
- ✅ **实时日志** - 实时显示执行进度
- ✅ **交易记录** - 完整保存所有交易哈希
- ✅ **跨平台** - Windows、Mac、Linux 均可使用

## 🚀 快速开始

### 方法 1: 本地运行（推荐）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动服务
python app.py

# 3. 打开浏览器
访问 http://localhost:5000
```

### 方法 2: 使用启动脚本

**Windows:**
```bash
启动.bat
```

**Mac/Linux:**
```bash
chmod +x start.sh
./start.sh
```

### 方法 3: 部署到云端

可以将应用部署到以下平台：
- Heroku
- Railway
- Render
- Vercel (需要适配)

## 📋 使用步骤

### 1. 连接钱包

1. 点击 "🔑 连接钱包"
2. 输入私钥
3. 点击 "连接"

### 2. 配置跨链参数

- **源链**: 选择发送链（如 Ethereum）
- **目标链**: 选择接收链（如 BSC）
- **单个金额**: 设置每个钱包的发送金额
- **余额**: 点击 "检查余额" 查看当前余额

### 3. 加载目标钱包

在文本框中输入钱包地址，每行一个：
```
0x2159864c15A8C0Bb74F3E9f57a4bfbAF5C46135b
0xb8eB8fc92143A590351356Ed8F64731660DA1606
```

或点击 "📋 加载示例" 查看示例格式。

### 4. 生成分发计划

点击 "📝 生成分发计划" 按钮。

### 5. 执行发送

点击 "💸 执行发送" 按钮，确认后即可开始跨链。

### 6. 查看结果

- 实时日志显示执行进度
- 结果表格显示每笔交易状态
- 点击 TxHash 可查看区块链浏览器详情
- 点击 "💾 导出结果" 保存 JSON 文件

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

## 🌐 部署到云端

### 部署到 Railway

1. 访问 [railway.app](https://railway.app)
2. 创建新项目
3. 连接 GitHub 仓库
4. 设置环境变量（如需要）
5. 自动部署

### 部署到 Render

1. 访问 [render.com](https://render.com)
2. 创建 "Web Service"
3. 连接 GitHub 仓库
4. 配置：
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
5. 部署

## ⚠️ 安全提示

### 重要提醒

- ⚠️ **私钥仅存储在服务器内存**
- ⚠️ **建议使用专用钱包，不要使用主钱包**
- ⚠️ **本地运行最安全**
- ⚠️ **云端部署需确保 HTTPS**
- ⚠️ **交易不可逆转**
- ⚠️ **自行承担风险**

### 安全最佳实践

1. **本地运行** - 最安全，私钥不出本地
2. **专用钱包** - 仅存放需要跨链的资金
3. **小额测试** - 首次使用建议 0.0005-0.001 ETH
4. **HTTPS** - 云端部署必须使用 HTTPS
5. **防火墙** - 限制访问 IP

## 🐛 故障排除

### 无法启动服务

**错误**: `ModuleNotFoundError: No module named 'flask'`

**解决**: 
```bash
pip install -r requirements.txt
```

### 连接钱包失败

**错误**: "私钥无效"

**解决**:
- 检查私钥格式（带或不带 0x 均可）
- 确保私钥正确

### 无法连接区块链

**错误**: "无法连接到 Ethereum"

**解决**:
- 检查网络连接
- 尝试切换网络或使用 VPN
- 等待几分钟后重试

### 交易失败

**错误**: "交易失败"

**解决**:
- 检查余额是否充足
- 检查 Gas 费用
- 在区块链浏览器查看详情

## 📊 API 接口

### POST /api/connect

连接钱包

```json
{
  "private_key": "your_private_key"
}
```

### POST /api/balance

获取余额

```json
{
  "chain": "Ethereum"
}
```

### POST /api/generate

生成分发计划

```json
{
  "wallets": ["0x...", "0x..."],
  "amount": 0.001,
  "origin_chain": "Ethereum",
  "dest_chain": "BSC"
}
```

### POST /api/execute

执行发送

```json
{}
```

### GET /api/status

获取状态

### GET /api/results

获取结果

### GET /api/logs

获取日志

## 💡 使用技巧

### 节省 Gas

- 选择低峰期：UTC 00:00-10:00
- 使用低 Gas 链：Base、Arbitrum
- 批量发送：一次性发送多个

### 提高效率

- 准备钱包列表文件
- 使用示例快速测试
- 实时日志监控进度

### 安全保障

- 定期导出交易记录
- 使用专用钱包
- 小额测试后再大额

## 🔗 相关链接

- [GitHub 仓库](https://github.com/LegionZYX/relay-cross-chain-distributor)
- [Relay API 文档](https://docs.relay.link/)
- [Etherscan](https://etherscan.io/)
- [BSCScan](https://bscscan.com/)

## 📞 技术支持

遇到问题？

1. 查看执行日志
2. 检查交易记录
3. 在区块链浏览器查询
4. 提交 GitHub Issue

---

**享受无缝的跨链体验！** 🚀

**⚠️ 重要提醒**: 首次使用请务必小额测试！
