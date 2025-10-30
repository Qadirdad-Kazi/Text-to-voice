@echo off
echo Setting up LiveKit Voice Agent...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.9 or higher.
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Node.js is not installed. Please install Node.js 18 or higher.
    exit /b 1
)

echo.
echo Setting up Backend...
cd server

REM Create virtual environment
echo Creating Python virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy env_template.txt .env
    echo Please edit server\.env with your API keys
)

cd ..

echo.
echo Setting up Frontend...
cd web

REM Install Node dependencies
echo Installing Node.js dependencies...
call npm install

REM Create .env.local if it doesn't exist
if not exist .env.local (
    echo Creating .env.local file...
    copy .env.example .env.local
    echo Please edit web\.env.local with your LiveKit URL
)

cd ..

echo.
echo Setup complete!
echo.
echo Next steps:
echo 1. Edit server\.env with your API keys
echo 2. Edit web\.env.local with your LiveKit URL
echo 3. Start the backend: cd server ^&^& venv\Scripts\activate ^&^& python main.py
echo 4. Start the frontend (in new terminal): cd web ^&^& npm run dev
echo.
echo Visit http://localhost:3000 to use the app!
pause

