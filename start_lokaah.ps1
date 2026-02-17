# LOKAAH Quick Start Script
# Run this to start the LOKAAH server with all dependencies loaded

Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "     Starting LOKAAH AI Tutoring Platform...         " -ForegroundColor White
Write-Host "========================================================`n" -ForegroundColor Cyan

# 1. Activate virtual environment
Write-Host "[1/3] Activating virtual environment..." -ForegroundColor Yellow
& "C:\Users\Lenovo\lokaah_app\.venv\Scripts\Activate.ps1"
Write-Host "      [OK] Virtual environment activated" -ForegroundColor Green

# 2. Add ffmpeg to PATH (if not already)
Write-Host "`n[2/3] Setting up ffmpeg..." -ForegroundColor Yellow
$ffmpegPath = "C:\Users\Lenovo\ffmpeg\ffmpeg-master-latest-win64-gpl\bin"
if ($env:Path -notlike "*$ffmpegPath*") {
    $env:Path += ";$ffmpegPath"
    Write-Host "      [OK] ffmpeg added to PATH" -ForegroundColor Green
} else {
    Write-Host "      [OK] ffmpeg already in PATH" -ForegroundColor Green
}

# 3. Start server
Write-Host "`n[3/3] Starting LOKAAH server..." -ForegroundColor Yellow
Write-Host "      Server will start on: http://localhost:8000" -ForegroundColor Cyan
Write-Host "      API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "      Press CTRL+C to stop`n" -ForegroundColor Gray
Write-Host "========================================================`n" -ForegroundColor Cyan

# Navigate to project directory
Set-Location "C:\Users\Lenovo\lokaah_app"

# Start the server
python main.py
