@echo off
echo ========================================
echo   LiveKit Voice Agent - Frontend
echo ========================================
echo.

cd /d "%~dp0\web"

REM Check if node_modules exists
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    echo.
)

REM Check if .env.local exists
if not exist ".env.local" (
    echo.
    echo Creating .env.local file...
    echo NEXT_PUBLIC_API_URL=http://localhost:8000 > .env.local
    echo NEXT_PUBLIC_LIVEKIT_URL=wss://placeholder.livekit.cloud >> .env.local
    echo.
    echo NOTE: .env.local created. Update LIVEKIT_URL if you have LiveKit configured.
    echo.
)

echo.
echo Starting frontend at http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

npm run dev


