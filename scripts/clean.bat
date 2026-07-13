@echo off
setlocal
cd /d "%~dp0\.."
rmdir /s /q build 2>nul
rmdir /s /q .pytest_cache 2>nul
for /d /r %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
del /s /q *.pyc 2>nul
echo Limpeza concluida.
