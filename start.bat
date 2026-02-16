@echo off
title Market Regime Detection Launcher
color 0B

echo ====================================================
echo   INITIALIZING MARKET REGIME DETECTION PROJECT
echo ====================================================

echo [0/2] Cleaning old processes...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1

echo [1/2] Backend at port 8000...
start "Backend (FastAPI)" cmd /k "cd backend && call venv\Scripts\activate && set PYTHONPATH=. && uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo [2/2] Frontend at port 5173...
start "Frontend (Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo ----------------------------------------------------
echo   ✅ Activated! 
echo ----------------------------------------------------
pause