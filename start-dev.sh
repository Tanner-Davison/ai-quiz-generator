#!/bin/bash

# Development startup script for AI Quiz Generator
echo "🚀 Starting AI Quiz Generator in development mode..."

# Check if we're in the right directory
if [ ! -f "start-dev.sh" ]; then
    echo "❌ Please run this script from the project root directory"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is available
if ! command_exists python3 && ! command_exists python; then
    echo "❌ Python is not installed or not in PATH"
    exit 1
fi

# Check if Node.js is available
if ! command_exists node; then
    echo "❌ Node.js is not installed or not in PATH"
    exit 1
fi

# Check if npm is available
if ! command_exists npm; then
    echo "❌ npm is not installed or not in PATH"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Copy environment files if they don't exist
if [ ! -f "backend/.env" ]; then
    echo "📝 Creating backend .env file from development template..."
    cp backend/env.development backend/.env
    echo "⚠️  Please edit backend/.env and add your GROQ_API_KEY"
fi

if [ ! -f "client/.env.local" ]; then
    echo "📝 Creating frontend .env.local file from development template..."
    cp client/env.development client/.env.local
fi

# Start backend in background
echo "🔧 Starting backend server..."
cd backend

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Using existing virtual environment"
    source venv/bin/activate
elif [ -d "venv_new" ]; then
    echo "📦 Using existing virtual environment (venv_new)"
    source venv_new/bin/activate
else
    echo "📦 Creating new virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "📦 Installing backend dependencies..."
    pip install -r requirements.txt
fi

# Start backend server
echo "🚀 Starting backend on http://localhost:8000"
python -m app.main &
BACKEND_PID=$!

cd ..

# Wait a moment for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Start frontend
echo "🎨 Starting frontend development server..."
cd client

# Install frontend dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

echo "🚀 Starting frontend on http://localhost:3000"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "🎉 Development servers started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping development servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait
