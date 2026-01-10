@echo off
chcp 65001 >nul
echo ========================================
echo   剪贴板历史管理器 - 打包脚本
echo ========================================
echo.

REM 清理旧的打包文件
if exist "build\" (
    echo 清理旧的build目录...
    rmdir /s /q "build"
)

if exist "dist\" (
    echo 清理旧的dist目录...
    rmdir /s /q "dist"
)

echo.
echo 开始打包...
echo.

REM 使用PyInstaller打包为单文件exe
pyinstaller --onefile --console --name="ClipboardManager" clipboard_manager.py

if errorlevel 1 (
    echo.
    echo ❌ 打包失败！
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✅ 打包成功！
echo ========================================
echo.
echo 可执行文件位置: dist\ClipboardManager.exe
echo.
echo 下一步: 运行 create_portable.bat 创建便携版发布包
echo.
pause
