@echo off
title Login Google Antigravity (Gemini 4 Argon & 3.8 Flash)
set "PATH=%LOCALAPPDATA%\omp;%USERPROFILE%\.local\bin;%APPDATA%\npm;%PATH%"

echo ==========================================================
echo    LOGIN GOOGLE ANTIGRAVITY (MENGAKTIFKAN GEMINI 4 ARGON)
echo ==========================================================
echo Jendela browser akan terbuka untuk login akun Google Anda.
echo.

if exist "%LOCALAPPDATA%\omp\omp.exe" (
    "%LOCALAPPDATA%\omp\omp.exe" login google-antigravity
) else if exist "%USERPROFILE%\.local\bin\omp.exe" (
    "%USERPROFILE%\.local\bin\omp.exe" login google-antigravity
) else (
    omp login google-antigravity
)

echo.
echo Jika login selesai, model Gemini 4 Argon dan Gemini 3.8 Flash sudah aktif!
pause
