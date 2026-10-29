@echo off
title Academic AI Agent (OMP - Gemini 4 Argon)
set "PATH=%LOCALAPPDATA%\omp;%USERPROFILE%\.local\bin;%APPDATA%\npm;%PATH%"

set "VAULT_DIR=%USERPROFILE%\Documents\Academic-Vault"
if not exist "%VAULT_DIR%" (
    mkdir "%VAULT_DIR%"
)
cd /d "%VAULT_DIR%"

echo ==========================================================
echo    Academic AI Agent (Gemini 4 Argon & 3.8 Flash)
echo    Lokasi Kerja: %CD%
echo ==========================================================
if exist "%LOCALAPPDATA%\omp\omp.exe" (
    "%LOCALAPPDATA%\omp\omp.exe" %*
) else if exist "%USERPROFILE%\.local\bin\omp.exe" (
    "%USERPROFILE%\.local\bin\omp.exe" %*
) else (
    omp %*
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [INFO] Jika OMP belum terpasang atau login dibutuhkan, jalankan setup.bat atau login-antigravity.bat
    pause
)
