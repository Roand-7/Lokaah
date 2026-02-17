@echo off
echo.
echo ==========================================
echo    LOKAAH Website - Local Server
echo ==========================================
echo.
echo Starting local server on port 8000...
echo.
echo Open your browser and visit:
echo    http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo.
cd web_lokaah
python -m http.server 8000
pause
