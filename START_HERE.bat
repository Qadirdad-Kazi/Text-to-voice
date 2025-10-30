@echo off
color 0A
echo.
echo ========================================
echo   LiveKit Voice Agent - Quick Start
echo ========================================
echo.
echo This will start both Backend and Frontend
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo ========================================
echo.

REM Start backend in new window
echo Starting Backend Server...
start "Backend Server - Port 8000" cmd /k "cd /d "%~dp0" && start_backend.bat"

REM Wait 3 seconds
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo Starting Frontend Server...
start "Frontend Server - Port 3000" cmd /k "cd /d "%~dp0" && start_frontend.bat"

echo.
echo ========================================
echo   Servers Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Two windows opened:
echo   1. Backend Server (Python/FastAPI)
echo   2. Frontend Server (Next.js)
echo.
echo Close those windows to stop the servers.
echo.
echo ========================================
pause


