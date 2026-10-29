@echo off
setlocal
cd /d "%~dp0"
title NEXUS-1 Launcher
chcp 65001 >nul

echo [1/4] Checking dependencies...
py -c "import torch, fastapi, uvicorn, httpx" 2>nul
if errorlevel 1 (
    echo Installing dependencies - first run only...
    py -m pip install -r requirements.txt --extra-index-url https://download.pytorch.org/whl/cpu
)

echo [2/4] Checking trained brain...
if not exist "checkpoints\nexus_brain.pt" py -m core.trainer

echo [3/4] Starting server on http://localhost:8000 ...
start "NEXUS-1 Server" /min py app.py

echo [4/4] Opening public tunnel...
py deploy\tunnel.py
pause
