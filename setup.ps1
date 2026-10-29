<#
==============================================================================
Agentic Workspace & Academic Starter Kit Setup Script for Windows
Stack: OMP (Oh-My-Pi) + Google Gemini + Obsidian + Curated Agent Skills
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
            Write-Host "[ERROR] Tidak dapat memasang OMP secara otomatis. Silakan pasang Node.js/npm dari https://nodejs.org/" -ForegroundColor Red
        }
    }
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
        omp login google-antigravity
        Write-Host "[SUCCESS] Login Google Antigravity selesai!" -ForegroundColor Green
    } catch {
        Write-Host "[WARN] Login belum selesai. Anda dapat menjalankannya nanti dengan perintah: 'omp login google-antigravity'" -ForegroundColor Yellow
    }
}

# 7. Pemeriksaan Companion Tools
Write-Host ""
Write-Host "[INFO] Memeriksa companion tools..." -ForegroundColor Cyan
if (Get-Command git -ErrorAction SilentlyContinue) {
    Write-Host "[SUCCESS] Git terdeteksi." -ForegroundColor Green
} else {
    Write-Host "[WARN] Git belum terpasang. Unduh dari: https://git-scm.com/download/win" -ForegroundColor Yellow
}

if (Get-Command typst -ErrorAction SilentlyContinue) {
    Write-Host "[SUCCESS] Typst terdeteksi." -ForegroundColor Green
} else {
    Write-Host "[INFO] Typst opsional. Pasang via winget: 'winget install Typst.Typst'" -ForegroundColor Cyan
}

if (Get-Command pandoc -ErrorAction SilentlyContinue) {
    Write-Host "[SUCCESS] Pandoc terdeteksi." -ForegroundColor Green
} else {
    Write-Host "[INFO] Pandoc opsional. Pasang via winget: 'winget install JohnMacFarlane.Pandoc'" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   ✅ SETUP WINDOWS SELESAI & SISTEM SIAP DIGUNAKAN!      " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Cara Menggunakan di Windows:"
Write-Host "1. Buka PowerShell di folder tugas akhir / vault Anda:"
Write-Host "   cd $TargetVault" -ForegroundColor Cyan
Write-Host "2. Jalankan OMP:"
Write-Host "   omp" -ForegroundColor Cyan
Write-Host "3. Buka aplikasi Obsidian -> Pilih 'Open folder as vault' -> Arahkan ke:"
Write-Host "   $TargetVault" -ForegroundColor Cyan
Write-Host ""
