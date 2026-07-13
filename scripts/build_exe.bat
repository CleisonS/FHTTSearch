@echo off
setlocal
cd /d "%~dp0\.."
if not exist ".venv\Scripts\activate.bat" (echo Execute scripts\install.bat primeiro.& pause& exit /b 1)
call ".venv\Scripts\activate.bat"
pip show pyinstaller >nul 2>nul || pip install pyinstaller
rmdir /s /q build 2>nul
rmdir /s /q dist\UNMInspector 2>nul
pyinstaller UNMInspector.spec --noconfirm
copy config.example.json dist\UNMInspector\ >nul
copy README.md dist\UNMInspector\ >nul
echo Executavel em dist\UNMInspector\UNMInspector.exe
