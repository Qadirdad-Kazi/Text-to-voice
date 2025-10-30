#!/bin/bash

echo "🚀 Setting up LiveKit Voice Agent..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

echo -e "${BLUE}📦 Setting up Backend...${NC}"
cd server

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp env_template.txt .env
    echo -e "${YELLOW}⚠️  Please edit server/.env with your API keys${NC}"
fi

cd ..

echo -e "${BLUE}📦 Setting up Frontend...${NC}"
cd web

# Install Node dependencies
echo "Installing Node.js dependencies..."
npm install

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "Creating .env.local file..."
    cp .env.example .env.local
    echo -e "${YELLOW}⚠️  Please edit web/.env.local with your LiveKit URL${NC}"
fi

cd ..

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit server/.env with your API keys"
echo "2. Edit web/.env.local with your LiveKit URL"
echo "3. Start the backend: cd server && source venv/bin/activate && python main.py"
echo "4. Start the frontend (in new terminal): cd web && npm run dev"
echo ""
echo "Visit http://localhost:3000 to use the app!"

