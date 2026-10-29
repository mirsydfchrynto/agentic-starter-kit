<#
==============================================================================
Agentic Workspace & Academic Starter Kit Setup Script for Windows
Stack: OMP (Oh-My-Pi) + Google Gemini + Obsidian + Curated Agent Skills
Fitur Khusus: Auto-PATH Injection (3-Level), Desktop Shortcut, Standalone Launcher
==============================================================================
#>

$ErrorActionPreference = "Stop"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   🤖 AGENTIC WORKSPACE & ACADEMIC STARTER KIT (WINDOWS)   " -ForegroundColor Cyan
Write-Host "   Powered by OMP, Google Gemini & Obsidian Vault         " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$UserHome = $env:USERPROFILE
$TargetVault = Join-Path $UserHome "Documents\Academic-Vault"

# 1. Menyiapkan struktur direktori di Windows
Write-Host "[INFO] Menyiapkan struktur direktori di $UserHome..." -ForegroundColor Cyan
$DirsToCreate = @(
    (Join-Path $UserHome ".omp\agent\skills"),
    (Join-Path $UserHome ".claude\skills"),
    (Join-Path $UserHome ".agents\skills"),
    (Join-Path $UserHome "Documents")
)

foreach ($dir in $DirsToCreate) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# 2. Instalasi atau verifikasi biner OMP (Oh-My-Pi) di Windows
Write-Host "[INFO] Memeriksa instalasi OMP..." -ForegroundColor Cyan
if (Get-Command omp -ErrorAction SilentlyContinue) {
    Write-Host "[SUCCESS] OMP sudah terpasang di sistem Windows." -ForegroundColor Green
} else {
    Write-Host "[INFO] Mengunduh dan memasang biner OMP untuk Windows..." -ForegroundColor Cyan
    try {
        Invoke-Expression (Invoke-RestMethod -Uri "https://omp.sh/install.ps1")
        Write-Host "[SUCCESS] OMP berhasil dipasang." -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Gagal memasang via script otomatis. Mencoba instalasi via npm/bun jika tersedia..." -ForegroundColor Yellow
        if (Get-Command npm -ErrorAction SilentlyContinue) {
            npm install -g @oh-my-pi/pi-coding-agent
            Write-Host "[SUCCESS] OMP berhasil dipasang via npm." -ForegroundColor Green
        } else {
            Write-Host "[ERROR] Tidak dapat memasang OMP secara otomatis. Silakan pasang Node.js dari https://nodejs.org/" -ForegroundColor Red
        }
    }
}

# 2.1 Deteksi Lokasi Biner OMP & Perbaikan PATH Otomatis (3-Level Auto-Fix)
Write-Host "[INFO] Memindai lokasi instalasi biner OMP..." -ForegroundColor Cyan
$PossibleDirs = @(
    (Join-Path $env:LOCALAPPDATA "omp"),
    (Join-Path $UserHome ".local\bin"),
    (Join-Path $env:APPDATA "npm")
)

$FoundOmpPath = ""
$FoundOmpDir = ""
foreach ($dir in $PossibleDirs) {
    $exeCheck = Join-Path $dir "omp.exe"
    $cmdCheck = Join-Path $dir "omp.cmd"
    if (Test-Path $exeCheck) {
        $FoundOmpPath = $exeCheck
        $FoundOmpDir = $dir
        break
    } elseif (Test-Path $cmdCheck) {
        $FoundOmpPath = $cmdCheck
        $FoundOmpDir = $dir
        break
    }
}

if (-not $FoundOmpPath -and (Get-Command omp -ErrorAction SilentlyContinue)) {
    $FoundOmpPath = (Get-Command omp).Source
    $FoundOmpDir = Split-Path -Parent $FoundOmpPath
}

if ($FoundOmpDir) {
    Write-Host "[SUCCESS] Biner OMP terverifikasi di: $FoundOmpPath" -ForegroundColor Green
    
    # Level 1: Injeksi ke sesi PowerShell saat ini
    if ($env:PATH -notlike "*$FoundOmpDir*") {
        $env:PATH = "$FoundOmpDir;$env:PATH"
    }
    
    # Level 2: Injeksi permanen ke User Environment Variables Windows (Registry)
    $UserPath = [Environment]::GetEnvironmentVariable("Path", "User")
    if ($UserPath -notlike "*$FoundOmpDir*") {
        [Environment]::SetEnvironmentVariable("Path", "$FoundOmpDir;$UserPath", "User")
        Write-Host "[SUCCESS] Berhasil mendaftarkan $FoundOmpDir ke User PATH Registry Windows." -ForegroundColor Green
    }
    
    # Level 3: Injeksi ke PowerShell Profile agar terminal baru otomatis mengenali perintah 'omp'
    try {
        $ProfileDir = Split-Path -Parent $PROFILE
        if (-not (Test-Path $ProfileDir)) {
            New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
        }
        $ProfileSnippet = "`$env:PATH = `"$FoundOmpDir;`$env:PATH`""
        if (-not (Test-Path $PROFILE) -or (Get-Content $PROFILE -Raw -ErrorAction SilentlyContinue) -notlike "*$FoundOmpDir*") {
            Add-Content -Path $PROFILE -Value "`n# OMP Auto-PATH Injected by Starter Kit`n$ProfileSnippet" -Force
            Write-Host "[SUCCESS] Injeksi PATH berhasil ditambahkan ke PowerShell Profile: $PROFILE" -ForegroundColor Green
        }
    } catch {
        # Abaikan jika ada pembatasan profile
    }
} else {
    Write-Host "[WARN] Lokasi direktori OMP belum terdeteksi. Launcher batch otomatis akan digunakan." -ForegroundColor Yellow
}

# 3. Sinkronisasi konfigurasi OMP & model Gemini
Write-Host "[INFO] Memasang konfigurasi OMP & model Gemini..." -ForegroundColor Cyan
$OmpConfigDir = Join-Path $UserHome ".omp\agent"
$ClaudeDir = Join-Path $UserHome ".claude"

Copy-Item -Path (Join-Path $ScriptDir "config\omp\config.yml") -Destination (Join-Path $OmpConfigDir "config.yml") -Force
Copy-Item -Path (Join-Path $ScriptDir "config\omp\models.yml") -Destination (Join-Path $OmpConfigDir "models.yml") -Force
Copy-Item -Path (Join-Path $ScriptDir "config\AGENTS.md") -Destination (Join-Path $OmpConfigDir "AGENTS.md") -Force
Copy-Item -Path (Join-Path $ScriptDir "config\AGENTS.md") -Destination (Join-Path $ClaudeDir "CLAUDE.md") -Force
Write-Host "[SUCCESS] Konfigurasi OMP, models.yml, dan AGENTS.md berhasil disinkronkan." -ForegroundColor Green

# 4. Salin seluruh Skills kurasi
Write-Host "[INFO] Menyinkronkan skills akademik dan rekayasa software..." -ForegroundColor Cyan
$SkillDestinations = @(
    (Join-Path $UserHome ".agents\skills"),
    (Join-Path $UserHome ".omp\agent\skills"),
    (Join-Path $UserHome ".claude\skills")
)

$AcademicSkills = Get-ChildItem -Path (Join-Path $ScriptDir "skills\academic") -Directory
$EngineeringSkills = Get-ChildItem -Path (Join-Path $ScriptDir "skills\engineering") -Directory
$AllSkills = $AcademicSkills + $EngineeringSkills

foreach ($skill in $AllSkills) {
    foreach ($dest in $SkillDestinations) {
        $destPath = Join-Path $dest $skill.Name
        Copy-Item -Path $skill.FullName -Destination $destPath -Recurse -Force
    }
}
Write-Host "[SUCCESS] Berhasil memasang $($AllSkills.Count) skills ke direktori agent." -ForegroundColor Green

# 5. Pasang Template Obsidian Academic Vault
if (Test-Path $TargetVault) {
    Write-Host "[WARN] Vault Obsidian sudah ada di: $TargetVault" -ForegroundColor Yellow
    Write-Host "[INFO] Melewati penimpaan file naskah untuk mencegah kehilangan data." -ForegroundColor Cyan
} else {
    Write-Host "[INFO] Memasang Template Obsidian Academic Vault ke: $TargetVault..." -ForegroundColor Cyan
    Copy-Item -Path (Join-Path $ScriptDir "vault-template") -Destination $TargetVault -Recurse -Force
    Write-Host "[SUCCESS] Vault Obsidian berhasil dipasang di $TargetVault." -ForegroundColor Green
}

# 5.1 Buat Launcher Batch Mandiri di Vault & Desktop (Solusi Anti-PATH Masalah)
Write-Host "[INFO] Menyiapkan launcher mandiri anti-masalah PATH..." -ForegroundColor Cyan
$VaultBat = Join-Path $TargetVault "start-omp.bat"
$VaultCmd = Join-Path $TargetVault "omp.cmd"

$OmpExecTarget = if ($FoundOmpPath) { "`"$FoundOmpPath`"" } else { "omp" }
$LauncherContent = @"
@echo off
title Academic AI Agent (OMP)
set "PATH=$FoundOmpDir;%LOCALAPPDATA%\omp;%USERPROFILE%\.local\bin;%APPDATA%\npm;%PATH%"
cd /d "%~dp0"
if exist "$FoundOmpPath" (
    "$FoundOmpPath" %*
) else (
    omp %*
)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Terjadi kendala saat meluncurkan OMP.
    pause
)
"@
Set-Content -Path $VaultBat -Value $LauncherContent -Force
Set-Content -Path $VaultCmd -Value $LauncherContent -Force

# Buat Desktop Shortcut langsung
$DesktopDir = [Environment]::GetFolderPath("Desktop")
if (Test-Path $DesktopDir) {
    $DesktopBat = Join-Path $DesktopDir "Buka Agent Skripsi.bat"
    $DesktopContent = @"
@echo off
title Academic AI Agent (OMP)
set "PATH=$FoundOmpDir;%LOCALAPPDATA%\omp;%USERPROFILE%\.local\bin;%APPDATA%\npm;%PATH%"
cd /d "$TargetVault"
if exist "$FoundOmpPath" (
    "$FoundOmpPath"
) else (
    omp
)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Terjadi kendala saat meluncurkan OMP.
    pause
)
"@
    Set-Content -Path $DesktopBat -Value $DesktopContent -Force
    Write-Host "[SUCCESS] Shortcut Desktop dibuat: '$DesktopBat'" -ForegroundColor Green
}

# 6. Pemeriksaan GEMINI_API_KEY di Windows Environment
Write-Host ""
Write-Host "--- PEMERIKSAAN KREDENSIAL API ---" -ForegroundColor Cyan
$CurrentApiKey = [Environment]::GetEnvironmentVariable("GEMINI_API_KEY", "User")
if (-not $CurrentApiKey) {
    $CurrentApiKey = $env:GEMINI_API_KEY
}

if (-not $CurrentApiKey) {
    Write-Host "[WARN] GEMINI_API_KEY belum terpasang di sistem Windows!" -ForegroundColor Yellow
    Write-Host "Dapatkan API Key dari https://aistudio.google.com/app/apikey" -ForegroundColor Yellow
    $UserKey = Read-Host "Masukkan Google Gemini API Key Anda sekarang (atau tekan Enter untuk lewat)"
    if ($UserKey -and $UserKey.Trim() -ne "") {
        [Environment]::SetEnvironmentVariable("GEMINI_API_KEY", $UserKey.Trim(), "User")
        $env:GEMINI_API_KEY = $UserKey.Trim()
        Write-Host "[SUCCESS] GEMINI_API_KEY berhasil disimpan permanen ke User Environment Variables Windows." -ForegroundColor Green
    }
} else {
    Write-Host "[SUCCESS] GEMINI_API_KEY terdeteksi aktif di sistem." -ForegroundColor Green
}

# 7. Opsi Login Google Antigravity (Gemini Pro, Claude Sonnet, dll)
Write-Host ""
Write-Host "--- LOGIN GOOGLE ANTIGRAVITY (OPSIONAL) ---" -ForegroundColor Cyan
Write-Host "Jika Anda memiliki akun dengan kuota Google Antigravity, Anda dapat login sekarang." -ForegroundColor Cyan
$LoginAntigravity = Read-Host "Apakah Anda ingin login ke Google Antigravity sekarang? (y/N)"
if ($LoginAntigravity -match "^[Yy]$") {
    try {
        if ($FoundOmpPath) {
            & "$FoundOmpPath" login google-antigravity
        } else {
            omp login google-antigravity
        }
        Write-Host "[SUCCESS] Login Google Antigravity selesai!" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Login belum selesai. Anda dapat menjalankannya nanti dengan: 'omp login google-antigravity'" -ForegroundColor Yellow
    }
}

# 8. Pemeriksaan Companion Tools
Write-Host ""
Write-Host "[INFO] Memeriksa companion tools..." -ForegroundColor Cyan
if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "[SUCCESS] Git terdeteksi." -ForegroundColor Green
} else {
    Write-Host "[WARN] Git belum terpasang. Unduh dari: https://git-scm.com/download/win" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   ✅ SETUP WINDOWS SELESAI & SISTEM SIAP DIGUNAKAN!      " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Cara Menggunakan (Pilih Yang Paling Mudah):"
Write-Host "1. CARA 1 (KLIK DESKTOP - TERIMA BERES):" -ForegroundColor Yellow
Write-Host "   Klik 2x file di Desktop Anda: 'Buka Agent Skripsi.bat'" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. CARA 2 (DARI TERMINAL POWERSHELL):" -ForegroundColor Yellow
Write-Host "   cd $TargetVault" -ForegroundColor Cyan
Write-Host "   omp" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. Buka aplikasi Obsidian -> Pilih 'Open folder as vault' -> Arahkan ke:"
Write-Host "   $TargetVault" -ForegroundColor Cyan
Write-Host ""
