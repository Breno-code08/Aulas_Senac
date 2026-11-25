@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Execute preparar_pc.bat antes de exportar.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" database_transfer.py export "%~dp0conectta-serra-backup.sql"
if errorlevel 1 (
    echo Exportacao falhou. Verifique se o MySQL do XAMPP esta iniciado.
    pause
    exit /b 1
)
echo Copie conectta-serra-backup.sql para o outro computador.
pause
