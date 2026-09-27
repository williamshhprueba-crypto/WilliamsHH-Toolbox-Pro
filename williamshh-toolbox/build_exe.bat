@echo off
REM ============================================================
REM  WilliamsHH Toolbox PRO - Genera el .exe en Windows
REM  Requisito: Python 3.10+ instalado (marca "Add to PATH")
REM  Uso: doble clic a este archivo y espera. El .exe sale en dist\
REM ============================================================
cd /d "%~dp0"
echo [1/3] Instalando dependencias...
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller
echo [2/3] Compilando WilliamsHH-Toolbox-PRO.exe ...
pyinstaller --noconfirm --onefile --windowed --clean --name "WilliamsHH-Toolbox-PRO" --icon "app\assets\icon.ico" --add-data "app\data;app\data" --add-data "app\assets;app\assets" "app\main.py"
echo [3/3] Listo. Tu programa esta en: dist\WilliamsHH-Toolbox-PRO.exe
pause
