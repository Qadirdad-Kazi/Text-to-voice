@echo off
echo ========================================
echo   LiveKit Voice Agent - Backend Server
echo ========================================
echo.

cd /d "%~dp0\server"

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv
    echo.
    echo Installing dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt
    echo.
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if .env exists
if not exist ".env" (
    echo.
    echo WARNING: .env file not found!
    echo The server may not work properly without API keys.
    echo Please create a .env file with your API keys.
    echo.
    pause
)

echo.
echo Starting server at http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

python main.py


