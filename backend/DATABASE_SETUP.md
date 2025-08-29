# PostgreSQL Database Setup Guide

This guide will help you set up PostgreSQL database for the AI Quiz Generator application.

## Prerequisites

- PostgreSQL 12 or higher installed
- Python 3.8+ with pip
- Virtual environment activated

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. PostgreSQL Setup

#### Option A: Using Docker (Recommended)

```bash
# Pull and run PostgreSQL container
docker run --name ai-quiz-postgres \
  -e POSTGRES_DB=ai_quiz_db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -p 5433:5432 \
  -d postgres:15

# Check if container is running
docker ps
```

**Note**: We use port 5433 to avoid conflicts with existing PostgreSQL installations.

#### Option B: Local Installation

1. Install PostgreSQL on your system
2. Create database and user:
```sql
CREATE DATABASE ai_quiz_db;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE ai_quiz_db TO postgres;
```

### 3. Environment Configuration

Create a `.env` file in the backend directory:

```bash
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
```

### 4. Database Migration

Initialize Alembic and create your first migration:

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Create initial migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

### 5. Verify Setup

Start the application:

```bash
python -m app.main
```

Check database health:
```bash
curl http://localhost:3000/health/database
```

## Database Schema

The application creates the following tables:

- **quizzes**: Stores quiz metadata
- **quiz_questions**: Stores individual quiz questions
- **quiz_submissions**: Stores quiz submissions
- **quiz_answers**: Stores user answers to questions
- **chat_sessions**: Stores chat conversation sessions
- **chat_messages**: Stores individual chat messages

## Troubleshooting

### Connection Issues

1. Verify PostgreSQL is running:
```bash
# Docker
docker ps | grep postgres

# Local
sudo systemctl status postgresql
```

2. Check connection string format:
```
postgresql+asyncpg://username:password@host:port/database
```

3. Test connection manually:
```bash
# For Docker setup (port 5433)
psql -h localhost -p 5433 -U postgres -d ai_quiz_db

# For local setup (port 5432)
psql -h localhost -U postgres -d ai_quiz_db
```

### Port Conflicts

If you get a "port already in use" error:

1. **Check what's using port 5432:**
```bash
sudo lsof -i :5432
# or
sudo netstat -tulpn | grep :5432
```

2. **Use our Docker setup with port 5433** (recommended):
```bash
docker-compose up -d postgres
```

3. **Or change your local PostgreSQL port** in postgresql.conf:
```
port = 5433
```

### Migration Issues

1. Reset migrations:
```bash
alembic downgrade base
alembic upgrade head
```

2. Check migration status:
```bash
alembic current
alembic history
```

## Development

### Adding New Models

1. Create model in `models/database_models.py`
2. Import in `database.py` init_db function
3. Generate migration: `alembic revision --autogenerate -m "Add new model"`
4. Apply migration: `alembic upgrade head`

### Database Operations

Use the provided service classes:
- `QuizService` for quiz operations
- `QuizSubmissionService` for submission operations
- `ChatSessionService` for chat operations

Example:
```python
from services.database_service import QuizService
from database import get_async_db

quiz_service = QuizService(Quiz)

@app.post("/quizzes/")
async def create_quiz(quiz_data: dict, db: AsyncSession = Depends(get_async_db)):
    return await quiz_service.create(db, quiz_data)
```

## Production Considerations

1. Use strong passwords
2. Enable SSL connections
3. Set up connection pooling
4. Configure backup strategies
5. Monitor database performance
6. Set appropriate connection limits
