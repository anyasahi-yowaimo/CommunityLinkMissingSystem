@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  echo Creating Python virtual environment...
  py -3.13 -m venv .venv
  if errorlevel 1 py -m venv .venv
  if errorlevel 1 (echo Python was not found. Install Python 3.11 or newer and retry.& pause & exit /b 1)
)
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
if errorlevel 1 (echo Dependency installation failed. Check internet and try again.& pause & exit /b 1)
set PYTHONPATH=%CD%\backend
python backend\scripts\seed_demo_data.py
if errorlevel 1 (echo Seed failed.& pause & exit /b 1)
echo.
echo LinkMissing is starting. Open http://127.0.0.1:8000
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000
pause
