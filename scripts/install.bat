@echo off
setlocal
cd /d "%~dp0\.."
python --version || (echo Python 3.11/3.12 nao encontrado.& exit /b 1)
if not exist ".venv" python -m venv ".venv"
call ".venv\Scripts\activate.bat" || exit /b 1
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
if errorlevel 1 pause & exit /b 1
echo Ambiente pronto. Execute scripts\run.bat
