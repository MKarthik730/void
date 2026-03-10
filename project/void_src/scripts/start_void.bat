@echo off
title VOID Ball
echo.
echo  Starting VOID Ball UI...
echo  ════════════════════════
echo  Make sure backend is running first!
echo  (Run start_backend.bat in another terminal)
echo.

:: Activate venv if present
if exist "%~dp0..\venv\Scripts\activate.bat" (
    call "%~dp0..\venv\Scripts\activate.bat"
)

cd /d "%~dp0..\frontend"
python void_ball.py

pause
