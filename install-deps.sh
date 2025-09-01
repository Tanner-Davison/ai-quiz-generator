#!/usr/bin/env bash

set -euo pipefail

WITH_DB=false
NO_ENV=false

print_usage() {
  cat <<'USAGE'
Usage: ./install-deps.sh [options]

Options:
  --with-db   Also start local Postgres via Docker Compose (detached)
  --no-env    Do not create .env files from templates
  -h, --help  Show this help message

This script installs backend (pip) and frontend (npm) dependencies without starting servers.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-db)
      WITH_DB=true
      shift
      ;;
    --no-env)
      NO_ENV=true
      shift
      ;;
    -h|--help)
      print_usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      print_usage
      exit 1
      ;;
  esac
done

command_exists() { command -v "$1" >/dev/null 2>&1; }

echo "\n🔎 Checking prerequisites..."
if ! command_exists python3 && ! command_exists python; then
  echo "❌ Python is not installed or not in PATH" >&2
  exit 1
fi
if ! command_exists node; then
  echo "❌ Node.js is not installed or not in PATH" >&2
  exit 1
fi
if ! command_exists npm; then
  echo "❌ npm is not installed or not in PATH" >&2
  exit 1
fi

PYTHON_CMD="python3"
if ! command_exists python3 && command_exists python; then
  PYTHON_CMD="python"
fi

echo "✅ Prereqs OK"

# Optional: create env files from templates
if [[ "$NO_ENV" == false ]]; then
  if [[ ! -f backend/.env ]]; then
    echo "📝 Creating backend .env from template (backend/env.development)"
    cp backend/env.development backend/.env
    echo "⚠️  Remember to set GROQ_API_KEY in backend/.env"
  fi
  if [[ ! -f client/.env.local ]]; then
    echo "📝 Creating frontend .env.local from template (client/env.development)"
    cp client/env.development client/.env.local
  fi
fi

echo "\n📦 Installing backend dependencies..."
pushd backend >/dev/null

# Prefer existing virtual env if present, otherwise create one
VENV_DIR=""
if [[ -d venv ]]; then
  VENV_DIR="venv"
elif [[ -d venv_new ]]; then
  VENV_DIR="venv_new"
else
  echo "📦 Creating Python virtual environment in backend/venv"
  $PYTHON_CMD -m venv venv
  VENV_DIR="venv"
fi

source "$VENV_DIR/bin/activate"
pip install --upgrade pip >/dev/null
pip install -r requirements.txt

popd >/dev/null

echo "\n📦 Installing frontend dependencies..."
pushd client >/dev/null
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi
popd >/dev/null

if [[ "$WITH_DB" == true ]]; then
  echo "\n🐘 Starting local Postgres (Docker Compose) ..."
  if ! command_exists docker && ! command_exists docker-compose; then
    echo "❌ Docker is not installed or not in PATH; cannot start database" >&2
    exit 1
  fi
  pushd backend >/dev/null
  if command_exists docker && docker compose version >/dev/null 2>&1; then
    docker compose up -d postgres
  elif command_exists docker-compose; then
    docker-compose up -d postgres
  else
    echo "❌ Couldn't find a working docker compose command" >&2
    popd >/dev/null
    exit 1
  fi
  popd >/dev/null
fi

echo "\n✅ All dependencies installed."
echo "- Backend venv: backend/$VENV_DIR"
echo "- Frontend node_modules: client/node_modules"
if [[ "$WITH_DB" == true ]]; then
  echo "- Postgres: running on localhost:5433 (container name: ai-quiz-postgres)"
fi
echo "\nYou can now start dev servers with:"
echo "  ./start-dev.sh"


