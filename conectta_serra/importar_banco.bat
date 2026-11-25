@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Execute preparar_pc.bat antes de importar.
    pause
    exit /b 1
)

set "BACKUP=%~1"
if "%BACKUP%"=="" set /p "BACKUP=Caminho do arquivo conectta-serra-backup.sql: "
if not exist "%BACKUP%" (
    echo Arquivo de backup nao encontrado: %BACKUP%
    pause
    exit /b 1
)

echo ATENCAO: a importacao substituira tabelas do banco conectta.
set /p "CONFIRM=Deseja continuar? Digite S para confirmar: "
if /i not "%CONFIRM%"=="S" exit /b 1

".venv\Scripts\python.exe" database_transfer.py import "%BACKUP%"
if errorlevel 1 (
    echo Importacao falhou. Confira o MySQL, DATABASE_URL e o arquivo de backup.
    pause
    exit /b 1
)
pause
