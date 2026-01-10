@echo off
chcp 65001 >nul
echo ========================================
echo   创建便携版发布包
echo ========================================
echo.

REM 检查是否已经打包
if not exist "dist\ClipboardManager.exe" (
    echo ❌ 未找到 ClipboardManager.exe
    echo 请先运行 build.bat 进行打包
    pause
    exit /b 1
)

REM 创建发布目录
set RELEASE_DIR=ClipboardManager_Portable
if exist "%RELEASE_DIR%\" (
    rmdir /s /q "%RELEASE_DIR%"
)

mkdir "%RELEASE_DIR%"

echo 正在创建便携版...
echo.

REM 复制可执行文件
copy "dist\ClipboardManager.exe" "%RELEASE_DIR%\" >nul
echo ✓ 已复制主程序

REM 创建使用说明
(
echo ========================================
echo   剪贴板历史管理器 - 使用说明
echo ========================================
echo.
echo 📋 功能介绍
echo -----------
echo 这是一个剪贴板历史管理工具，可以记录您复制的所有内容
echo 并通过双击鼠标右键快速访问和粘贴历史记录
echo.
echo 🚀 快速开始
echo -----------
echo 1. 双击 ClipboardManager.exe 启动程序
echo 2. 程序会在后台运行，监控您的复制操作
echo 3. 正常复制文本（Ctrl+C）
echo 4. 在任意输入框双击鼠标右键（快速点击两次）
echo 5. 从弹出菜单中选择要粘贴的内容
echo.
echo 💡 使用技巧
echo -----------
echo - 程序会自动保存最近20条复制记录
echo - 历史记录会保存到 clipboard_config.json
echo - 可以将程序添加到开机自启动文件夹
echo - 按 Ctrl+C 可退出程序
echo.
echo ⚙️ 开机自启动设置
echo -----------
echo 方法1: 使用提供的脚本
echo    双击运行 "添加到开机启动.bat"
echo.
echo 方法2: 手动设置
echo    1. 按 Win+R 打开运行
echo    2. 输入: shell:startup
echo    3. 将 ClipboardManager.exe 的快捷方式复制到该文件夹
echo.
echo 📌 注意事项
echo -----------
echo - 首次运行可能需要允许防火墙权限
echo - 只记录文本内容，不支持图片等格式
echo - 菜单失去焦点或按ESC会自动关闭
echo.
echo 🔧 常见问题
echo -----------
echo Q: 双击右键没反应？
echo A: 确保两次点击间隔在0.5秒内
echo.
echo Q: 粘贴没反应？
echo A: 确保目标是可输入的文本框且光标已聚焦
echo.
echo Q: 如何卸载？
echo A: 直接删除程序文件夹即可，如已添加开机启动请运行"取消开机启动.bat"
echo.
echo ========================================
echo 版本: 1.0.0
echo 技术支持: GitHub Issues
echo ========================================
) > "%RELEASE_DIR%\使用说明.txt"
echo ✓ 已创建使用说明

REM 创建开机启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo set TARGET="%%~dp0ClipboardManager.exe"
echo set STARTUP_FOLDER=%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Startup
echo.
echo if not exist %%TARGET%% ^(
echo     echo ❌ 未找到程序文件！
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo 正在添加到开机启动...
echo.
echo REM 创建快捷方式
echo set SCRIPT="%%TEMP%%\create_shortcut.vbs"
echo echo Set oWS = WScript.CreateObject^("WScript.Shell"^) ^> %%SCRIPT%%
echo echo sLinkFile = "%%STARTUP_FOLDER%%\ClipboardManager.lnk" ^>^> %%SCRIPT%%
echo echo Set oLink = oWS.CreateShortcut^(sLinkFile^) ^>^> %%SCRIPT%%
echo echo oLink.TargetPath = %%TARGET%% ^>^> %%SCRIPT%%
echo echo oLink.WorkingDirectory = "%%~dp0" ^>^> %%SCRIPT%%
echo echo oLink.Description = "剪贴板历史管理器" ^>^> %%SCRIPT%%
echo echo oLink.Save ^>^> %%SCRIPT%%
echo.
echo cscript //nologo %%SCRIPT%%
echo del %%SCRIPT%%
echo.
echo echo.
echo echo ✅ 已成功添加到开机启动！
echo echo.
echo echo 程序会在下次开机时自动运行
echo echo.
echo pause
) > "%RELEASE_DIR%\添加到开机启动.bat"
echo ✓ 已创建开机启动脚本

REM 创建取消开机启动脚本
(
echo @echo off
echo chcp 65001 ^>nul
echo set STARTUP_FILE="%%APPDATA%%\Microsoft\Windows\Start Menu\Programs\Startup\ClipboardManager.lnk"
echo.
echo if exist %%STARTUP_FILE%% ^(
echo     del %%STARTUP_FILE%%
echo     echo ✅ 已取消开机启动
echo ^) else ^(
echo     echo ℹ️  未找到开机启动项
echo ^)
echo.
echo pause
) > "%RELEASE_DIR%\取消开机启动.bat"
echo ✓ 已创建取消启动脚本

REM 创建启动脚本
(
echo @echo off
echo start "" "%%~dp0ClipboardManager.exe"
) > "%RELEASE_DIR%\启动程序.bat"
echo ✓ 已创建启动脚本

echo.
echo ========================================
echo ✅ 便携版创建成功！
echo ========================================
echo.
echo 发布目录: %RELEASE_DIR%\
echo.
echo 文件列表:
echo   - ClipboardManager.exe         (主程序)
echo   - 使用说明.txt                 (详细说明)
echo   - 添加到开机启动.bat           (自启动工具)
echo   - 取消开机启动.bat             (取消自启动)
echo   - 启动程序.bat                 (快速启动)
echo.
echo 您可以将整个 %RELEASE_DIR% 文件夹复制到任何电脑使用！
echo.
pause
