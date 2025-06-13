@echo off
echo Building executable...
pip install pyinstaller
pyinstaller app.spec --clean
echo Build complete!
echo Executable location: dist\AI-Resume-Analyzer.exe
pause