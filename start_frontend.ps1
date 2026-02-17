# Start Frontend Server
# Serves the web_lokaah static files on port 5500

Write-Host "🚀 Starting LOKAAH Frontend on http://localhost:5500" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend UI: http://localhost:5500" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

Set-Location web_lokaah
python -m http.server 5500
