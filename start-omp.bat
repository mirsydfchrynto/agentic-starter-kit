@echo off
title Academic AI Agent (OMP)
set "PATH=%LOCALAPPDATA%\omp;%USERPROFILE%\.local\bin;%APPDATA%\npm;%PATH%"

set "VAULT_DIR=%USERPROFILE%\Documents\Academic-Vault"
if not exist "%VAULT_DIR%" (
    mkdir "%VAULT_DIR%"
)
cd /d "%VAULT_DIR%"

echo Membuka Agentic Workspace di: %CD%
if exist "%LOCALAPPDATA%\omp\omp.exe" (
    "%LOCALAPPDATA%\omp\omp.exe" %*
) else if exist "%USERPROFILE%\.local\bin\omp.exe" (
    "%USERPROFILE%\.local\bin\omp.exe" %*
) else (
    omp %*
)

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [INFO] Jika OMP belum ditemukan, jalankan .\setup.bat terlebih dahulu.
    pause
)
