# AI Quiz Generator

An AI-powered quiz generation web app. Enter any topic, choose your settings, and get a multiple-choice quiz generated in seconds using Groq's LLM API. Optionally enhance questions with real Wikipedia content for more grounded, factual quizzes.

## Tech Stack

**Frontend** — React 19, TypeScript, Vite, React Router v7

**Backend** — FastAPI, SQLAlchemy (async), PostgreSQL, Alembic, Groq API

**Deployment** — Vercel (frontend), Railway (backend)

## Features

- Generate multiple-choice quizzes on any topic via Groq LLM
- Optional Wikipedia enhancement for factually grounded questions
- Submit answers and receive instant scoring with per-question feedback
- Quiz history with submission statistics stored in PostgreSQL
- Auto-detects environment (development / production) for CORS and DB config

## Project Structure

```
ai-test-generator/
├── client/                  # React + TypeScript frontend (Vite)
│   └── src/
│       ├── components/      # UI components (QuizSection, QuestionCard, ResultsSection, etc.)
│       ├── services/        # API service layer
│       ├── types/           # Shared TypeScript types
│       └── config/          # Environment config
│
├── backend/                 # FastAPI Python backend
│   └── app/
│       ├── routes/          # API route handlers (quiz, wikipedia, health)
│       ├── services/        # Business logic (quiz generation, DB services)
│       ├── models/          # SQLAlchemy DB models + Pydantic schemas
│       ├── middleware/       # CORS and request logging
│       ├── database.py      # Async DB connection and session management
│       └── config.py        # Environment-based settings
│
├── start-dev.sh             # One-command dev startup (Linux/macOS)
├── start-dev.ps1            # One-command dev startup (Windows)
└── install-deps.sh          # Install all dependencies
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/quiz/generate` | Generate a new quiz for a given topic |
| `POST` | `/quiz/submit` | Submit answers and receive scored results |
| `GET`  | `/quiz/history` | List all past quizzes with statistics |
| `GET`  | `/quiz/history/{id}` | Get full details for a specific quiz |
| `GET`  | `/wikipedia/...` | Wikipedia content endpoints for enhancement |
| `GET`  | `/health` | Health check |

Interactive API docs available at `http://localhost:8000/docs` when running locally.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (or use the mock DB setup script)
- A [Groq API key](https://console.groq.com)

### Quick Start (Linux/macOS)

```bash
# Clone the repo
git clone <repo-url>
cd ai-test-generator

# Install all dependencies
./install-deps.sh

# Start both servers
./start-dev.sh
```

The script will:
- Create a Python virtual environment and install backend deps
- Copy environment templates if `.env` files don't exist
- Start the FastAPI backend on `http://localhost:8000`
- Start the Vite frontend on `http://localhost:5173`

### Quick Start (Windows)

```powershell
./start-dev.ps1
```

### Manual Setup

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.development .env        # Then add your GROQ_API_KEY
python -m app.main
```

**Frontend:**
```bash
cd client
cp env.development .env.local
npm install
npm run dev
```

### Environment Variables

**Backend (`backend/.env`):**
```env
ENVIRONMENT=development
GROQ_API_KEY=your_groq_api_key_here
DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_quiz_dev
DEBUG=true
PORT=8000
```

**Frontend (`client/.env.local`):**
```env
VITE_API_URL=http://localhost:8000
```

### Database Setup

Run migrations with Alembic:
```bash
cd backend
alembic upgrade head
```

Or use the mock database setup script for local development without PostgreSQL:
```bash
./setup-mock-database.sh
```

## Deployment

The app is configured for Vercel + Railway out of the box.

- `client/vercel.json` — Vercel frontend config
- `backend/Procfile` — Railway process definition
- `railway.json` — Railway service config

Set production environment variables in your Vercel and Railway dashboards matching the keys above.

## License

Copyright © 2025 Tanner Davison. All Rights Reserved.
