@echo off
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Install Python 3.10 or newer and enable Add Python to PATH.
  pause
  exit /b 1
)
echo Starting Intent Lock. Open http://127.0.0.1:8000/ in your browser.
echo Keep this window open while using the demo.
python server.py
if errorlevel 1 (
  echo.
  echo The server could not start. Read the error above.
  pause
)
