@echo off
chcp 65001 >nul
echo ============================================================
echo CF Bypass Crawler Pro - Windows一键安装脚本
echo 适配国内镜像，自动安装所有依赖
echo ============================================================

echo.
echo 【1/4】升级pip（国内清华源）...
pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo ❌ pip升级失败，请检查Python环境
    pause
    exit /b 1
)

echo.
echo 【2/4】安装Python依赖...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo.
echo 【3/4】安装Playwright浏览器驱动（国内镜像）...
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright/
playwright install chromium
if errorlevel 1 (
    echo ❌ 浏览器驱动安装失败
    pause
    exit /b 1
)

echo.
echo 【4/4】创建空代理文件...
if not exist proxies.txt (
    type nul > proxies.txt
    echo ✅ 创建空代理文件 proxies.txt
)

echo.
echo ============================================================
echo ✅ 所有依赖安装完成！
echo 📌 运行程序：python main.py
echo 📌 如需使用代理，请编辑 proxies.txt 文件
echo ============================================================
pause
