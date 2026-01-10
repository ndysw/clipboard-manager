@echo off
chcp 65001 >nul
echo ========================================
echo   剪贴板历史管理器
echo ========================================
echo.
echo 正在启动程序...
echo.

python clipboard_manager.py

if errorlevel 1 (
    echo.
    echo ❌ 程序运行出错!
    echo.
    echo 可能的原因:
    echo 1. 未安装 Python
    echo 2. 未安装依赖包
    echo.
    echo 解决方法:
    echo 1. 安装 Python 3.7+
    echo 2. 运行: pip install -r requirements.txt
    echo.
    pause
)
