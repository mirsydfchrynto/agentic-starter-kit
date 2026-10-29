@echo off
title Agentic Workspace Setup (Windows)
echo ==========================================================
echo    Menjalankan instalasi Agentic Workspace (Windows)
echo ==========================================================
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Terjadi kendala saat menjalankan setup.ps1
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ==========================================================
echo    Instalasi Berhasil! 
echo    Tinggal klik 2x icon 'Buka Agent Skripsi.bat' di Desktop!
echo ==========================================================
pause
