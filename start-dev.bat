@echo off
echo Starting LiveKit Voice Agent in development mode...

REM Start backend in new window
echo Starting backend server...
start "Backend Server" cmd /k "cd server && venv\Scripts\activate && python main.py"

REM Wait a bit for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend in new window
echo Starting frontend server...
start "Frontend Server" cmd /k "cd web && npm run dev"

echo.
echo Servers started!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo.
echo Close the command windows to stop the servers
pause

