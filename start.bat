@echo off
setlocal
cd /d %~dp0
if not exist .venv\Scripts\python.exe call install.bat
call .venv\Scripts\activate
if not exist .env copy .env.example .env
python -m app.cli setup >nul
start "" http://127.0.0.1:8000
echo AltAlpha is starting at http://127.0.0.1:8000
echo On the first run, data synchronization starts automatically in the background.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
