@echo off
title TELLUM ULTIMUM
cd /d "%~dp0"

where python >nul 2>&1
if errorlevel 1 (
    echo Python was not found on your PATH.
    echo Install Python from https://python.org and run: pip install -r requirements.txt
    pause
    exit /b 1
)

echo Starting TELLUM ULTIMUM...
echo Close this window to stop the app.
echo.

python -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo Streamlit failed to start. Try: pip install -r requirements.txt
    pause
)
