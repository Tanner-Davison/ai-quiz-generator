# Development startup script for AI Quiz Generator (Windows PowerShell)
Write-Host "🚀 Starting AI Quiz Generator in development mode..." -ForegroundColor Green

if (-not (Test-Path "start-dev.ps1")) {
    Write-Host "❌ Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Function to check if a command exists
function Test-Command($cmdname) {
    return [bool](Get-Command -Name $cmdname -ErrorAction SilentlyContinue)
}

# Check if Python is available
if (-not (Test-Command "python") -and -not (Test-Command "python3")) {
    Write-Host "❌ Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if Node.js is available
if (-not (Test-Command "node")) {
    Write-Host "❌ Node.js is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check if npm is available
if (-not (Test-Command "npm")) {
    Write-Host "❌ npm is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Prerequisites check passed" -ForegroundColor Green

# Copy environment files if they don't exist
if (-not (Test-Path "backend\.env")) {
    Write-Host "📝 Creating backend .env file from development template..." -ForegroundColor Cyan
    Copy-Item "backend\env.development" "backend\.env"
    Write-Host "⚠️  Please edit backend\.env and add your GROQ_API_KEY" -ForegroundColor Yellow
}

if (-not (Test-Path "client\.env.local")) {
    Write-Host "📝 Creating frontend .env.local file from development template..." -ForegroundColor Cyan
    Copy-Item "client\env.development" "client\.env.local"
}

# Start backend in background
Write-Host "🔧 Starting backend server..." -ForegroundColor Yellow
Set-Location backend

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "📦 Using existing virtual environment" -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path "venv_new") {
    Write-Host "📦 Using existing virtual environment (venv_new)" -ForegroundColor Cyan
    & "venv_new\Scripts\Activate.ps1"
} else {
    Write-Host "📦 Creating new virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    Write-Host "📦 Installing backend dependencies..." -ForegroundColor Cyan
    pip install -r requirements.txt
}

# Start backend server
Write-Host "🚀 Starting backend on http://localhost:8000" -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "python" -ArgumentList "-m", "app.main"
$backendProcess = Get-Process | Where-Object { $_.ProcessName -eq "python" } | Select-Object -Last 1

Set-Location ..

# Wait a moment for backend to start
Write-Host "⏳ Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Start frontend
Write-Host "🎨 Starting frontend development server..." -ForegroundColor Yellow
Set-Location client

# Install frontend dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Installing frontend dependencies..." -ForegroundColor Cyan
    npm install
}

Write-Host "🚀 Starting frontend on http://localhost:3000" -ForegroundColor Green
Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run", "dev"
$frontendProcess = Get-Process | Where-Object { $_.ProcessName -eq "node" } | Select-Object -Last 1

Set-Location ..

Write-Host ""
Write-Host "🎉 Development servers started!" -ForegroundColor Green
Write-Host "📱 Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "🔧 Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Yellow

# Function to cleanup on exit
function Stop-DevServers {
    Write-Host ""
    Write-Host "🛑 Stopping development servers..." -ForegroundColor Yellow
    
    if ($backendProcess) {
        Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    
    if ($frontendProcess) {
        Stop-Process -Id $frontendProcess.Id -Force -ErrorAction SilentlyContinue
    }
    
    Write-Host "✅ Servers stopped" -ForegroundColor Green
}

# Set up cleanup on script exit
try {
    # Wait for user to press Ctrl+C
    Write-Host "Press Ctrl+C to stop servers..." -ForegroundColor Yellow
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    Stop-DevServers
}
