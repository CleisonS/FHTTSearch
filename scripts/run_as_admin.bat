@echo off
setlocal
cd /d "%~dp0\.."
echo Solicitando elevacao administrativa para o UNM Inspector...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process -FilePath '%~dp0run.bat' -Verb RunAs"
if errorlevel 1 pause
