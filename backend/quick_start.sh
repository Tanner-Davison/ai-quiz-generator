#!/bin/bash

echo "🚀 AI Quiz Generator - Quick Start Script"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# API Configuration
PORT=3000
HOST=0.0.0.0

# Groq Configuration
GROQ_API_KEY=your_groq_api_key_here

# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5433/ai_quiz_db
DATABASE_SYNC_URL=postgresql://postgres:password@localhost:5433/ai_quiz_db

# AI Service Configuration
DEFAULT_TEMPERATURE=0.7
DEFAULT_MAX_TOKENS=1024
DEFAULT_QUIZ_MAX_TOKENS=1024

# Wikipedia Service Configuration
MAX_WIKIPEDIA_SUMMARY_LENGTH=1000

# CORS Configuration
ALLOWED_ORIGINS=["*"]
EOF
    echo "✅ .env file created. Please update GROQ_API_KEY with your actual key."
else
    echo "✅ .env file already exists"
    echo "📝 Updating .env file with new database port..."
    # Update existing .env file with new port
    sed -i 's/localhost:5432/localhost:5433/g' .env
    echo "✅ Database port updated to 5433"
fi

# Start PostgreSQL with Docker Compose
echo "🐘 Starting PostgreSQL database on port 5433..."
docker-compose up -d postgres

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
until docker exec ai-quiz-postgres pg_isready -U postgres -d ai_quiz_db > /dev/null 2>&1; do
    echo "   Waiting for PostgreSQL..."
    sleep 2
done
echo "✅ Database is ready!"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "   Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python init_db.py

echo ""
echo "🎉 Setup complete! Your database is ready."
echo ""
echo "📋 Next steps:"
echo "   1. Update GROQ_API_KEY in .env file"
echo "   2. Start the application: python -m app.main"
echo "   3. Access API docs: http://localhost:3000/docs"
echo "   4. Check database health: http://localhost:3000/health/database"
echo ""
echo "🐘 Database management:"
echo "   - Database running on port 5433 (changed from 5432 to avoid conflicts)"
echo "   - Stop database: docker-compose down"
echo "   - View logs: docker-compose logs postgres"
echo "   - Access pgAdmin: http://localhost:5050 (admin@example.com / admin)"
echo "   - Connect directly: psql -h localhost -p 5433 -U postgres -d ai_quiz_db"
