@REM This script builds the executable for the VUT IVP Solver Comparison project using PyInstaller.
@echo off
REM Enable virtual environment
call .venv\Scripts\activate

REM Clear previous builds
rmdir /s /q build
rmdir /s /q dist
del /q main.spec

REM Build the executable with PyInstaller and include the CSV file
pyinstaller --onefile --windowed --add-data "IVP_problems.csv;." --name "VUT IVP Solver Comparison" main.py

REM Copy the CSV file next to the .exe in the dist folder
copy IVP_problems.csv dist\

echo.
echo Build completed. The executable and CSV file are located in the 'dist' folder.
pause