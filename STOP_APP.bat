@echo off
title Jyotish - Stop All Services
color 0C
echo.
echo  Stopping Jyotish App 3.0 services...
echo.
taskkill /f /fi "WINDOWTITLE eq Jyotish-Backend*" >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq Jyotish-Video-Server*" >nul 2>&1

for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| find ":8080 " ^| find "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| find ":5000 " ^| find "LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo  All Jyotish services stopped!
echo.
timeout /t 2 /nobreak >nul
