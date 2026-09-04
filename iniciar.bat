@echo off
cd /d %~dp0
start "CraftPixel backend" ".venv\Scripts\python.exe" -m uvicorn main:app --app-dir backend --port 8000
start "CraftPixel frontend" ".venv\Scripts\python.exe" -m http.server 5500 --directory frontend
timeout /t 2 >nul
start "" "http://127.0.0.1:5500/index.html"
