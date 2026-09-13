@echo off
REM Countdown Web App Startup Script for Windows
REM This script starts the countdown web application

setlocal enabledelayedexpansion

set APP_NAME=countdown_web
set PORT=5000

echo.
echo ========================================
echo Countdown Web Application Startup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check dependencies
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Flask is not installed
    echo Please run: pip install -r requirements-web.txt
    pause
    exit /b 1
)

REM Check if LINE token is set
if "!LINE_CHANNEL_ACCESS_TOKEN!"=="" (
    echo WARNING: LINE_CHANNEL_ACCESS_TOKEN environment variable is not set
    echo The application may not work properly without it.
    echo Please set it using: set LINE_CHANNEL_ACCESS_TOKEN=your_token_here
    echo.
)

echo Starting %APP_NAME%.py...
echo.
echo Access the web interface at: http://localhost:%PORT%
echo Press Ctrl+C to stop the server
echo.

python %APP_NAME%.py

pause
