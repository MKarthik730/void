@echo off
title VOID Backend Server
echo.
echo  ██╗   ██╗ ██████╗ ██╗██████╗
echo  ██║   ██║██╔═══██╗██║██╔══██╗
echo  ██║   ██║██║   ██║██║██║  ██║
echo  ╚██╗ ██╔╝██║   ██║██║██║  ██║
echo   ╚████╔╝ ╚██████╔╝██║██████╔╝
echo    ╚═══╝   ╚═════╝ ╚═╝╚═════╝
echo.
echo  AI Assistant Backend - Starting...
echo  ════════════════════════════════
echo.

:: Set HuggingFace cache to D: drive
set HF_HOME=D:\huggingface
set HUGGINGFACE_HUB_CACHE=D:\huggingface\hub

:: Activate venv if present
if exist "%~dp0..\venv\Scripts\activate.bat" (
    call "%~dp0..\venv\Scripts\activate.bat"
    echo  [OK] Virtual environment activated
)

echo  [OK] HF cache set to D:\huggingface
echo  [..] Starting FastAPI on http://localhost:8000
echo.

cd /d "%~dp0..\backend"
uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause
