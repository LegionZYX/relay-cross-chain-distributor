@echo off
chcp 65001 >nul
echo ========================================================================
echo  Relay Cross-Chain Distributor - Web Version
echo ========================================================================
echo.
echo 正在启动 Web 服务...
echo.

python -c "import flask" 2>nul
if errorlevel 1 (
    echo 正在安装依赖...
    pip install -r requirements.txt
)

echo.
echo 启动浏览器...
echo 访问地址：http://localhost:5000
echo.
echo 按 Ctrl+C 停止服务
echo.
echo ========================================================================
echo.

start http://localhost:5000
python app.py

pause
