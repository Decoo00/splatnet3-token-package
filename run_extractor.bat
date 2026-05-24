@echo off
title SplatNet 3 Token Extractor Starter

cd /d "%~dp0"

echo ==================================================
echo  SplatNet 3 Token Extractor (100% Portable Edition)
echo ==================================================
echo.
echo Verifying standalone python environment and launching GUI...
echo Please wait a moment...
echo.
pause

if exist "python_env\python.exe" (
    start /b python_env\python.exe main_gui.py
    pause
) else (
    echo [ERROR] Embedded Python environment (python_env\pythonw.exe) is missing.
    echo Please make sure you have extracted the ZIP file completely.
    pause
)

pause