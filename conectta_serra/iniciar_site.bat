@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Execute preparar_pc.bat antes de iniciar o site.
    pause
    exit /b 1
)

powershell -NoProfile -Command "if (-not (Test-NetConnection 127.0.0.1 -Port 3306 -InformationLevel Quiet)) { exit 1 }"
if errorlevel 1 (
    echo MySQL nao esta respondendo na porta 3306.
    echo Abra o XAMPP Control Panel e inicie MySQL antes de iniciar o site.
    pause
    exit /b 1
)

start "" "http://127.0.0.1:5000/"
".venv\Scripts\python.exe" iniciar.py
pause
