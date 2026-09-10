@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>nul
if errorlevel 1 (
  echo Python n'est pas installe ou n'est pas dans le PATH.
  echo Installe Python 3.11+ depuis https://www.python.org/downloads/windows/
  pause
  exit /b 1
)

echo Installation de pygame et PyInstaller...
py -m pip install --upgrade pygame pyinstaller
if errorlevel 1 (
  echo Echec de l'installation des dependances.
  pause
  exit /b 1
)

echo Construction de Ashenveil.exe...
py -m PyInstaller --noconfirm --clean --onefile --windowed --name Ashenveil --add-data "assets;assets" ashenveil.py
if errorlevel 1 (
  echo Echec de la construction.
  pause
  exit /b 1
)

echo.
echo Termine. Le fichier est ici : dist\Ashenveil.exe
start "" "%~dp0dist"
pause
