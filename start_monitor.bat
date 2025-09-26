@echo off
echo Starting Commission Statement Auto-Monitor...
echo.
echo This will monitor the 'docs' folder for new commission statements
echo and automatically process them using AI-powered extraction.
echo.
echo Loading configuration from .env file...
echo.
echo Press Ctrl+C to stop monitoring.
echo.
pause
python monitor_commissions.py
pause