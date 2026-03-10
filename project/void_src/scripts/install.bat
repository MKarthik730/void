@echo off
title VOID Setup
echo.
echo  VOID — Installing Dependencies
echo  ════════════════════════════════
echo.

:: Create virtual environment
python -m venv venv
call venv\Scripts\activate.bat
echo  [OK] Virtual environment created

:: Upgrade pip
pip install --upgrade pip

:: Install backend
echo.
echo  [..] Installing backend dependencies...
pip install -r backend\requirements.txt
echo  [OK] Backend dependencies installed

:: Install frontend
echo.
echo  [..] Installing frontend dependencies...
pip install -r frontend\requirements.txt
echo  [OK] Frontend dependencies installed

echo.
echo  ════════════════════════════════════════
echo  Setup complete!
echo.
echo  Next steps:
echo  1. Run database\setup.sql in PostgreSQL
echo  2. Add your GEMINI_API_KEY to backend\.env
echo  3. Run scripts\start_backend.bat
echo  4. Run scripts\start_void.bat
echo  ════════════════════════════════════════
echo.
pause
