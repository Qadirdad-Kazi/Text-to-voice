@echo off
echo Starting LiveKit Voice Agent Backend...
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Starting FastAPI server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python main.py

pause


