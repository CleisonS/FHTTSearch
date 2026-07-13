@echo off
setlocal
cd /d "%~dp0\.."
if not exist ".venv\Scripts\activate.bat" (echo Execute scripts\install.bat primeiro.& pause& exit /b 1)
call ".venv\Scripts\activate.bat"
python main.py
if errorlevel 1 pause
