@echo off
title Smart City - Lanceur Backend + Frontend
echo ========================================================
echo   Demarrage de la plateforme Smart City Qualite de l'Air
echo ========================================================

echo [1/2] Lancement du Backend FastAPI sur http://localhost:8080 ...
start "Smart City - Backend FastAPI (8080)" cmd /k "cd /d "%~dp0Back\api" && .venv\Scripts\uvicorn.exe main:app --reload --host 0.0.0.0 --port 8080"

echo [2/2] Lancement du Frontend React sur http://localhost:5173 ...
start "Smart City - Frontend React (5173)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo Les deux serveurs sont lances dans deux fenetres separees :
echo   - Application Web : http://localhost:5173
echo   - Documentation API Swagger : http://localhost:8080/docs
pause
