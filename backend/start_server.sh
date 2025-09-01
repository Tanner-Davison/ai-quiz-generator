#!/bin/bash
cd /home/tanner/projects/react/ai-test-generator/backend

# Check if virtual environment exists
if [ -d "venv_new" ]; then
    echo "📦 Using venv_new virtual environment"
    source venv_new/bin/activate
elif [ -d "venv" ]; then
    echo "📦 Using venv virtual environment"
    source venv/bin/activate
else
    echo "❌ No virtual environment found. Please run quick_start.sh first."
    exit 1
fi

echo "🚀 Starting AI Quiz Generator server..."
python3 -m app.main
