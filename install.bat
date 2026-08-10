@echo off
setlocal
cd /d %~dp0
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3.11+ is required. Install Python and rerun install.bat.
  exit /b 1
)
if not exist .venv py -3 -m venv .venv
call .venv\Scripts\activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e .
if not exist .env copy .env.example .env
python -m app.cli setup
echo.
echo AltAlpha installed successfully. Run start.bat.
