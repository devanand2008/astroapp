@echo off
setlocal EnableDelayedExpansion
title JYOTISH 3.0 - GitHub Push
color 0B

set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"

echo.
echo  ================================================
echo   JYOTISH 3.0 - GitHub Push
echo  ================================================
echo.

where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed or not in PATH.
    echo         Install Git from https://git-scm.com/download/win
    pause
    exit /b 1
)

cd /d "%ROOT%"

git config --global user.email "devanand2008@gmail.com"
git config --global user.name "Devanand"
git config --global init.defaultBranch main

if not exist ".git" (
    git init
    git branch -M main
)

echo [1/5] Staging files...
git add .
if exist "backend\astro_seed.db" git add -f "backend\astro_seed.db"

echo.
echo [2/5] Files ready:
git status --short

echo.
set /p COMMIT_MSG="Commit message [Deploy Jyotish app to Render]: "
if "%COMMIT_MSG%"=="" set "COMMIT_MSG=Deploy Jyotish app to Render"

git diff --cached --quiet
if errorlevel 1 (
    echo.
    echo [3/5] Creating commit...
    git commit -m "%COMMIT_MSG%"
) else (
    echo.
    echo [3/5] Nothing new to commit.
)

echo.
echo [4/5] GitHub repository URL
echo.
echo First create the repository in GitHub if it does not exist:
echo https://github.com/new
echo.
echo Repository name: jyotish-app
echo Account: devanand2008
echo Do not add README, gitignore, or license on GitHub.
echo.
set /p REPO_URL="Paste repo URL, for example https://github.com/devanand2008/jyotish-app.git : "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL provided.
    pause
    exit /b 1
)

rem Normalize a common paste mistake: remove a trailing slash.
if "%REPO_URL:~-1%"=="/" set "REPO_URL=%REPO_URL:~0,-1%"

git remote remove origin 2>nul
git remote add origin "%REPO_URL%"
git branch -M main

echo.
echo Current remote:
git remote -v

echo.
echo [5/5] Pushing to GitHub...
echo Complete browser authentication if Git asks.
git push -u origin main

if errorlevel 1 (
    echo.
    echo [ERROR] Push failed.
    echo.
    echo Fix checklist:
    echo 1. Open https://github.com/devanand2008/jyotish-app
    echo 2. If it says 404, create it at https://github.com/new
    echo 3. Make sure you are signed in as devanand2008 or an account with access.
    echo 4. Run this file again and paste the repo URL once.
    echo.
    pause
    exit /b 1
)

echo.
echo  ================================================
echo   SUCCESS - Code pushed to GitHub
echo  ================================================
echo.
echo  Repo: %REPO_URL%
echo.
start "" "%REPO_URL%"
pause
