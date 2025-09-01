#!/usr/bin/env bash

set -euo pipefail

WITH_DB=false
NO_ENV=false
INSTALL_PREREQS=false

print_usage() {
  cat <<'USAGE'
Usage: ./install-deps.sh [options]

Options:
  --with-db         Also start local Postgres via Docker Compose (detached)
  --no-env          Do not create .env files from templates
  --install-prereqs Install missing prerequisites (Python, Node.js, Docker)
  -h, --help        Show this help message

This script installs backend (pip) and frontend (npm) dependencies without starting servers.
With --install-prereqs, it can also install Python, Node.js, and Docker if missing.
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
    --install-prereqs)
      INSTALL_PREREQS=true
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

detect_os() {
  if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if command_exists apt; then
      echo "ubuntu"
    elif command_exists yum; then
      echo "rhel"
    elif command_exists pacman; then
      echo "arch"
    else
      echo "linux"
    fi
  elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "macos"
  elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    echo "windows"
  else
    echo "unknown"
  fi
}

install_python() {
  local os=$(detect_os)
  echo "📦 Installing Python..."
  case $os in
    ubuntu)
      sudo apt update && sudo apt install -y python3 python3-pip python3-venv
      ;;
    rhel)
      sudo yum install -y python3 python3-pip
      ;;
    arch)
      sudo pacman -S python python-pip
      ;;
    macos)
      if command_exists brew; then
        brew install python
      else
        echo "❌ Please install Homebrew first: https://brew.sh" >&2
        exit 1
      fi
      ;;
    *)
      echo "❌ Unsupported OS for auto Python install. Please install Python manually." >&2
      exit 1
      ;;
  esac
}

install_nodejs() {
  local os=$(detect_os)
  echo "📦 Installing Node.js..."
  case $os in
    ubuntu)
      curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
      sudo apt install -y nodejs
      ;;
    rhel)
      curl -fsSL https://rpm.nodesource.com/setup_lts.x | sudo bash -
      sudo yum install -y nodejs
      ;;
    arch)
      sudo pacman -S nodejs npm
      ;;
    macos)
      if command_exists brew; then
        brew install node
      else
        echo "❌ Please install Homebrew first: https://brew.sh" >&2
        exit 1
      fi
      ;;
    *)
      echo "❌ Unsupported OS for auto Node.js install. Please install Node.js manually." >&2
      exit 1
      ;;
  esac
}

install_docker() {
  local os=$(detect_os)
  echo "📦 Installing Docker..."
  case $os in
    ubuntu)
      sudo apt update
      sudo apt install -y ca-certificates curl gnupg lsb-release
      sudo mkdir -p /etc/apt/keyrings
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
      sudo apt update
      sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
      sudo systemctl start docker
      sudo systemctl enable docker
      sudo usermod -aG docker $USER
      echo "⚠️  You may need to log out and back in for Docker group membership to take effect"
      ;;
    rhel)
      sudo yum install -y yum-utils
      sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
      sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
      sudo systemctl start docker
      sudo systemctl enable docker
      sudo usermod -aG docker $USER
      echo "⚠️  You may need to log out and back in for Docker group membership to take effect"
      ;;
    arch)
      sudo pacman -S docker docker-compose
      sudo systemctl start docker
      sudo systemctl enable docker
      sudo usermod -aG docker $USER
      echo "⚠️  You may need to log out and back in for Docker group membership to take effect"
      ;;
    macos)
      if command_exists brew; then
        brew install --cask docker
        echo "⚠️  Please start Docker Desktop from Applications folder"
      else
        echo "❌ Please install Homebrew first: https://brew.sh" >&2
        exit 1
      fi
      ;;
    *)
      echo "❌ Unsupported OS for auto Docker install. Please install Docker manually." >&2
      exit 1
      ;;
  esac
}

echo -e "\n🔎 Checking prerequisites..."

# Check and install Python
if ! command_exists python3 && ! command_exists python; then
  if [[ "$INSTALL_PREREQS" == true ]]; then
    install_python
  else
    echo "❌ Python is not installed. Use --install-prereqs to auto-install" >&2
    exit 1
  fi
fi

# Check and install Node.js
if ! command_exists node; then
  if [[ "$INSTALL_PREREQS" == true ]]; then
    install_nodejs
  else
    echo "❌ Node.js is not installed. Use --install-prereqs to auto-install" >&2
    exit 1
  fi
fi

# npm should come with Node.js, but double-check
if ! command_exists npm; then
  echo "❌ npm is not installed (should come with Node.js)" >&2
  exit 1
fi

# Check Docker (only if --with-db is specified)
if [[ "$WITH_DB" == true ]] && ! command_exists docker; then
  if [[ "$INSTALL_PREREQS" == true ]]; then
    install_docker
  else
    echo "❌ Docker is not installed. Use --install-prereqs to auto-install" >&2
    exit 1
  fi
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

echo -e "\n📦 Installing backend dependencies..."
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

echo -e "\n📦 Installing frontend dependencies..."
pushd client >/dev/null
if [[ -f package-lock.json ]]; then
  npm ci
else
  npm install
fi
popd >/dev/null

if [[ "$WITH_DB" == true ]]; then
  echo -e "\n🐘 Starting local Postgres (Docker Compose) ..."
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

echo -e "\n✅ All dependencies installed."
echo "- Backend venv: backend/$VENV_DIR"
echo "- Frontend node_modules: client/node_modules"
if [[ "$WITH_DB" == true ]]; then
  echo "- Postgres: running on localhost:5433 (container name: ai-quiz-postgres)"
fi
echo -e "\nYou can now start dev servers with:"
echo "  ./start-dev.sh"
