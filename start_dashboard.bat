@echo off
REM Start the Job Hunt Dashboard
REM This script activates the virtual environment and runs the Flask app

cd /d C:\Users\johnj\OneDrive\Documents\VS_projects\dashboard

REM Activate the virtual environment
call C:\Users\johnj\OneDrive\Documents\VS_projects\Prohram_IDE_files\dashboard_venv\Scripts\activate.bat

REM Start the Flask app
python main.py

REM Keep window open if there's an error
pause
