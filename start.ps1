# LOKAAH Quick Start Script
# Run this to start both backend and frontend

Write-Host "🚀 Starting LOKAAH..." -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "   Please copy .env.example to .env and fill in your API keys" -ForegroundColor Yellow
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "❌ Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Run: python -m venv .venv" -ForegroundColor Yellow
    Write-Host "   Then: .\.venv\Scripts\activate" -ForegroundColor Yellow
    Write-Host "   Then: pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Environment checks passed" -ForegroundColor Green
Write-Host ""

# Start Backend in background
Write-Host "📡 Starting Backend Server..." -ForegroundColor Cyan
$backendJob = Start-Job -ScriptBlock {
    Set-Location $using:PWD
    & ".\.venv\Scripts\python.exe" main.py
}

Write-Host "   Backend server starting (Job ID: $($backendJob.Id))..." -ForegroundColor Gray

# Wait for backend to start
Write-Host "   Waiting for server to be ready..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Check if backend is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend server is running on http://localhost:8000" -ForegroundColor Green
    Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor Gray
} catch {
    Write-Host "⚠️  Backend might still be starting..." -ForegroundColor Yellow
    Write-Host "   Check manually at: http://localhost:8000" -ForegroundColor Gray
}

Write-Host ""

# Start Frontend
Write-Host "🌐 Starting Frontend Server..." -ForegroundColor Cyan
Write-Host "   Frontend will be available at: http://localhost:5500" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop all servers" -ForegroundColor Yellow
Write-Host ""

# Start frontend in foreground (so Ctrl+C works)
Set-Location web_lokaah
try {
    python -m http.server 5500
} finally {
    # Cleanup: Stop backend when frontend is stopped
    Write-Host ""
    Write-Host "🛑 Stopping servers..." -ForegroundColor Yellow
    Stop-Job -Job $backendJob
    Remove-Job -Job $backendJob
    Write-Host "✅ All servers stopped" -ForegroundColor Green
}
