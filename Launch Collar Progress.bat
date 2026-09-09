@echo off
title Collar Journey
cd /d "%~dp0"
echo.
echo  Collar Journey - Cap d'Agde 14-day tracker
echo  Starting... browser will open shortly.
echo.
python -m pip install -q -r collar_requirements.txt
python -m streamlit run collar_progress.py --server.port 8502
pause
