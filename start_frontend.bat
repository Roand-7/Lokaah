@echo off
REM Start Frontend Server on port 5500

echo.
echo ========================================
echo   LOKAAH Frontend Server
echo ========================================
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:5500
echo.
echo Press Ctrl+C to stop the server
echo.

cd web_lokaah
python -m http.server 5500
