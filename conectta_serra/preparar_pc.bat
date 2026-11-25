@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
    echo Python nao encontrado. Instale Python 3.12 ou superior em https://www.python.org/downloads/
    echo Marque "Add python.exe to PATH" durante a instalacao.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente Python...
    py -3 -m venv .venv
    if errorlevel 1 goto failed
)

echo Instalando dependencias...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed

echo.
echo Preparacao concluida. Inicie o MySQL pelo XAMPP e execute iniciar_site.bat.
pause
exit /b 0

:failed
echo.
echo A preparacao falhou. Confira se Python 3.12+ e internet estao disponiveis.
pause
exit /b 1
