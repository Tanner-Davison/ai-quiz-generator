# AI Quiz Generator

A full-stack web application that generates educational quizzes using AI, with a FastAPI backend and React frontend, featuring PostgreSQL database persistence.

## 🏗️ Project Architecture

```
ai-test-generator/
├── backend/                 # FastAPI Python backend
│   ├── app/
│   │   ├── main.py         # FastAPI app entry point
│   │   ├── config.py       # Configuration & environment variables
│   │   ├── database.py     # Database connection & session management
│   │   ├── middleware/     # CORS, logging middleware
│   │   ├── models/         # Pydantic & SQLAlchemy models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic & AI integration
│   │   └── utils/          # Utility functions
│   ├── alembic/            # Database migrations
│   ├── requirements.txt    # Python dependencies
│   └── docker-compose.yml  # PostgreSQL container setup
└── client/                 # React TypeScript frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── types/          # TypeScript type definitions
    │   └── utils/          # Frontend utilities
    └── package.json        # Node.js dependencies
```

## 🚀 How It Works

### 1. **Frontend (React + TypeScript)**
- User enters a topic (e.g., "Python Loops")
- Frontend sends POST request to `/quiz/generate`
- Displays generated quiz with multiple choice questions
- User takes quiz and submits answers
- Shows results and score

### 2. **Backend (FastAPI + PostgreSQL)**
- Receives quiz generation request
- Calls Groq AI API to generate quiz content
- Saves quiz and questions to PostgreSQL database
- Returns structured quiz data to frontend
- Handles quiz submissions and scoring

### 3. **Database (PostgreSQL)**
- Stores all generated quizzes
- Persists quiz questions and answers
- Tracks user submissions and scores
- Maintains chat session history

## 🔑 Key Components to Study

### **Backend Architecture (High Priority)**

#### **Database Layer (`app/database.py`)**
```python
# Study these concepts:
- SQLAlchemy async engine setup
- Session management with dependency injection
- Database connection lifecycle (startup/shutdown)
- Table creation with Base.metadata.create_all
```

#### **Models (`app/models/`)**
```python
# Two types of models to understand:
1. Pydantic models (quiz.py, chat.py) - API request/response schemas
2. SQLAlchemy models (database_models.py) - Database table definitions
```

#### **Services (`app/services/`)**
```python
# Business logic layer:
- ai_service.py: Groq AI API integration
- quiz_service.py: Quiz generation logic
- database_service.py: Generic CRUD operations
```

#### **Routes (`app/routes/`)**
```python
# API endpoints:
- quiz.py: Quiz generation and submission
- health.py: Health checks and system status
- chat.py: Chat functionality (if implemented)
```

### **Frontend Architecture (Medium Priority)**

#### **Components (`client/src/components/`)**
```typescript
// Study the component hierarchy:
- TopicInputSection: User input for quiz topics
- QuizSection: Quiz display and interaction
- QuestionCard: Individual question rendering
- ResultsSection: Score display and results
```

#### **State Management**
```typescript
// Understand how data flows:
- API calls to backend
- Local state management
- Component prop passing
```

### **Database Design (High Priority)**

#### **Table Structure**
```sql
-- Core tables to understand:
quizzes: id, topic, model, temperature, created_at
quiz_questions: id, quiz_id, question, options, correct_answer, explanation
quiz_submissions: id, quiz_id, user_id, score, percentage
quiz_answers: id, submission_id, question_id, user_answer, is_correct
```

#### **Relationships**
```sql
-- Foreign key relationships:
quiz_questions.quiz_id → quizzes.id
quiz_submissions.quiz_id → quizzes.id
quiz_answers.submission_id → quiz_submissions.id
quiz_answers.question_id → quiz_questions.id
```

## 🧠 Core Concepts to Master

### **1. FastAPI Framework**
- **Dependency Injection**: How `Depends(get_async_db)` works
- **Pydantic Models**: Request/response validation
- **Async/Await**: Asynchronous database operations
- **Middleware**: CORS, logging, error handling

### **2. SQLAlchemy ORM**
- **Async Sessions**: `AsyncSession` vs regular `Session`
- **Model Relationships**: How tables connect to each other
- **CRUD Operations**: Create, Read, Update, Delete patterns
- **Migrations**: Alembic for schema changes

### **3. Database Design**
- **Normalization**: Why we separate quizzes and questions
- **Foreign Keys**: How relationships maintain data integrity
- **Indexing**: Performance considerations
- **Transactions**: ACID properties and rollbacks

### **4. API Design**
- **RESTful Endpoints**: HTTP methods and status codes
- **Error Handling**: Graceful failure and user feedback
- **Validation**: Input sanitization and type checking
- **Documentation**: Auto-generated OpenAPI docs

## 🔧 Development Workflow

### **1. Local Development**
```bash
# Start PostgreSQL
docker-compose up -d postgres

# Run backend
cd backend && python -m app.main

# Run frontend
cd client && npm run dev
```

### **2. Database Changes**
```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### **3. Testing Endpoints**
```bash
# Health check
curl http://localhost:3000/health

# Generate quiz
curl -X POST "http://localhost:3000/quiz/generate" \
  -H "Content-Type: application/json" \
  -d '{"topic": "JavaScript", "model": "llama3-8b-8192"}'
```

## 📚 Study Order (Recommended)

### **Week 1: Backend Fundamentals**
1. Study `app/main.py` - understand FastAPI app setup
2. Study `app/config.py` - configuration management
3. Study `app/database.py` - database connections
4. Study `app/models/database_models.py` - table structure

### **Week 2: API & Services**
1. Study `app/routes/quiz.py` - API endpoints
2. Study `app/services/quiz_service.py` - business logic
3. Study `app/services/ai_service.py` - external API integration
4. Study `app/services/database_service.py` - CRUD operations

### **Week 3: Frontend & Integration**
1. Study React component structure
2. Study API integration patterns
3. Study state management
4. Test full user flow

### **Week 4: Advanced Topics**
1. Study database migrations (Alembic)
2. Study error handling and logging
3. Study performance optimization
4. Study deployment considerations

## 🎯 Key Questions to Answer

### **Architecture Questions**
- Why did we separate Pydantic and SQLAlchemy models?
- How does dependency injection work in FastAPI?
- Why use async/await for database operations?
- How do the frontend and backend communicate?

### **Database Questions**
- Why store questions separately from quizzes?
- How do foreign keys maintain data integrity?
- What happens if a quiz is deleted?
- How would you add user authentication?

### **Scalability Questions**
- How would you handle multiple users?
- What if the AI service is slow?
- How would you cache frequently requested quizzes?
- What database optimizations would you implement?

## 🚀 Next Steps for Learning

### **Immediate (This Week)**
1. Run the application locally
2. Generate a few quizzes
3. Check the database to see saved data
4. Read through the code comments

### **Short Term (Next 2 Weeks)**
1. Add a new API endpoint
2. Modify the database schema
3. Add input validation
4. Implement error handling

### **Long Term (Next Month)**
1. Add user authentication
2. Implement quiz analytics
3. Add more AI models
4. Deploy to production

## 💡 Pro Tips

1. **Use the FastAPI docs**: Visit `http://localhost:3000/docs` to see interactive API documentation
2. **Check the logs**: Backend logs show exactly what's happening
3. **Database exploration**: Use `psql` to explore your data structure
4. **Incremental learning**: Don't try to understand everything at once

## 🔍 Debugging Tools

- **Backend logs**: Check console output for detailed information
- **Database queries**: Use `docker exec` to run `psql` commands
- **API testing**: Use the FastAPI docs or `curl` commands
- **Frontend dev tools**: Browser console and React dev tools

This project demonstrates modern full-stack development with AI integration, database design, and clean architecture. Focus on understanding the flow of data from user input → AI generation → database storage → user response.
# ai-quiz-generator
# ai-quiz-generator
