@echo off
chcp 65001 >nul
set STARTUP_FILE="%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ClipboardManager.lnk"

if exist %STARTUP_FILE% (
    del %STARTUP_FILE%
    echo ✅ 已取消开机启动
) else (
    echo ℹ️  未找到开机启动项
)

echo.
pause
