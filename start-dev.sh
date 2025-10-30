#!/bin/bash

# Start both backend and frontend in development mode

echo "🚀 Starting LiveKit Voice Agent in development mode..."

# Function to cleanup background processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

trap cleanup EXIT INT TERM

# Start backend
echo "Starting backend server..."
cd server
source venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend server..."
cd web
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Servers started!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for any process to exit
wait

