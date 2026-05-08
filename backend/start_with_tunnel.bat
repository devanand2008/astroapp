@echo off
title JYOTISH 3.0 - Backend Server
color 0A

echo.
echo  ██╗   ██╗██╗   ██╗ ██████╗ ████████╗██╗███████╗██╗  ██╗
echo  ██║   ██║╚██╗ ██╔╝██╔═══██╗╚══██╔══╝██║██╔════╝██║  ██║
echo  ██║   ██║ ╚████╔╝ ██║   ██║   ██║   ██║███████╗███████║
echo  ██║   ██║  ╚██╔╝  ██║   ██║   ██║   ██║╚════██║██╔══██║
echo  ╚██████╔╝   ██║   ╚██████╔╝   ██║   ██║███████║██║  ██║
echo   ╚═════╝    ╚═╝    ╚═════╝    ╚═╝   ╚═╝╚══════╝╚═╝  ╚═╝
echo.
echo  JYOTISH 3.0 - Tamil Vedic Astrology Platform
echo  Backend + Tunnel Launcher
echo  ================================================
echo.

:: Move to backend directory
cd /d "%~dp0"

:: Activate virtual environment
if exist "venv312\Scripts\activate.bat" (
    call venv312\Scripts\activate.bat
    echo [OK] Virtual environment activated: venv312
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo [OK] Virtual environment activated: venv
) else (
    echo [WARN] No virtual environment found. Using system Python.
)

echo.
echo  Starting FastAPI backend on port 8080...
echo  Local URL : http://localhost:8080
echo.

:: Start uvicorn in background using start
start "JYOTISH Backend" cmd /k "uvicorn main:app --host 0.0.0.0 --port 8080 --reload"

timeout /t 3 /nobreak >nul

:: Check if ngrok is installed
where ngrok >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo  [OK] ngrok detected. Starting tunnel...
    echo  Copy the ngrok HTTPS URL and set it in the GitHub Pages app:
    echo.
    echo    In browser console on your GitHub Pages site, run:
    echo    setJyotishBackend("https://YOUR-NGROK-URL.ngrok-free.app")
    echo.
    start "JYOTISH ngrok Tunnel" cmd /k "ngrok http 8080"
) else (
    echo  [INFO] ngrok not found. Backend is only accessible on local network.
    echo.
    echo  To access from GitHub Pages on other devices:
    echo    1. Install ngrok: https://ngrok.com/download
    echo    2. Run: ngrok http 8080
    echo    3. Copy the https URL and run in browser console:
    echo       setJyotishBackend("https://YOUR-NGROK-URL.ngrok-free.app")
    echo.
    echo  OR use your local IP (same WiFi network only):
    for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
        set LOCAL_IP=%%a
        goto :show_ip
    )
    :show_ip
    echo    setJyotishBackend("http://%LOCAL_IP: =%:8080")
    echo.
)

echo  ================================================
echo  Backend is running! Press Ctrl+C in the
echo  "JYOTISH Backend" window to stop.
echo  ================================================
pause
