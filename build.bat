@echo off
chcp 65001 >nul
echo ================================================
echo     AI简历分析系统 - 可执行文件构建工具
echo ================================================
echo.

echo 正在检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

echo.
echo 正在安装构建依赖...
pip install pyinstaller
if errorlevel 1 (
    echo 警告: PyInstaller安装可能失败，继续尝试构建...
)

echo.
echo 正在运行构建脚本...
python build_exe.py

echo.
echo 构建完成！
echo 可执行文件位于 dist\AI简历分析系统\ 目录中
echo.
pause