@echo off
chcp 65001 >nul
set TARGET="%~dp0ClipboardManager.exe"
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

if not exist %TARGET% (
    echo ❌ 未找到程序文件！
    pause
    exit /b 1
)

echo 正在添加到开机启动...
echo.

REM 创建快捷方式
set SCRIPT="%TEMP%\create_shortcut.vbs"
echo Set oWS = WScript.CreateObject("WScript.Shell") > %SCRIPT%
echo sLinkFile = "%STARTUP_FOLDER%\ClipboardManager.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = %TARGET% >> %SCRIPT%
echo oLink.WorkingDirectory = "%~dp0" >> %SCRIPT%
echo oLink.Description = "剪贴板历史管理器" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript //nologo %SCRIPT%
del %SCRIPT%

echo.
echo ✅ 已成功添加到开机启动！
echo.
echo 程序会在下次开机时自动运行
echo.
pause
