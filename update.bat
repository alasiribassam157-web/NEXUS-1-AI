@echo off
setlocal
cd /d "%~dp0"
title NEXUS-1 Update
chcp 65001 >nul
set "GIT=git"
where git >nul 2>nul || set "GIT=C:\Program Files\Git\cmd\git.exe"

echo [1/3] Running smoke tests...
py -m tests.smoke_test
if errorlevel 1 (
    echo Tests failed - nothing was pushed. Fix the errors and try again.
    pause
    exit /b 1
)

echo [2/3] Saving changes...
set /p "MSG=Describe your change: "
if "%MSG%"=="" set "MSG=Update NEXUS-1"
"%GIT%" add -A
"%GIT%" commit -m "%MSG%"

echo [3/3] Pushing to GitHub...
"%GIT%" push
echo.
echo Done. GitHub is updated and Render redeploys the live link automatically in a few minutes.
pause
