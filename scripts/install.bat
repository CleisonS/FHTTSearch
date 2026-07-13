@echo off
setlocal
cd /d "%~dp0\.."
python -c "import sys; raise SystemExit(0 if sys.version_info[:2] in [(3,11),(3,12)] else 1)" || (
  echo Python 3.11 ou 3.12 nao encontrado.
  pause
  exit /b 1
)
if not exist ".venv" python -m venv ".venv"
if errorlevel 1 pause & exit /b 1
call ".venv\Scripts\activate.bat" || exit /b 1
python -m pip install --upgrade pip
pip install -r requirements.txt -r requirements-dev.txt
if errorlevel 1 (
  echo Falha ao instalar dependencias.
  pause
  exit /b 1
)
echo Ambiente pronto. Execute scripts\run.bat
