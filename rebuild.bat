@echo off
chcp 65001 >nul
echo 正在重新构建可执行文件...
echo 检查PyInstaller是否已安装...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
)
echo 开始构建...
pyinstaller app.spec --clean
if errorlevel 1 (
    echo 构建失败！请检查错误信息。
    pause
    exit /b 1
)
echo 构建完成！
echo 可执行文件位置: dist\AI简历分析系统.exe
echo 文件大小:
dir "dist\AI简历分析系统.exe" | find "AI简历分析系统.exe"
echo.
echo 可以运行以下命令测试:
echo python test_exe.py
echo.
pause