@echo off
:: Comprobar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python no esta instalado. Descargalo de python.org
    start https://www.python.org/downloads/
    pause
    exit
)

:: Ejecutar el script
python windows_pdf_wizard.py
pause
