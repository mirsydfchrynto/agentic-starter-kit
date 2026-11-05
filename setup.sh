#!/usr/bin/env bash
# ==============================================================================
# Agentic Workspace & Academic Starter Kit Setup Script
# Stack: OMP (Oh-My-Pi) + Google Antigravity & Free Chinese Models + Obsidian
# ==============================================================================

set -e

# ANSI Color codes
BOLD="\033[1m"
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
CYAN="\033[0;36m"
RED="\033[0;31m"
RESET="\033[0m"

log_info() {
    echo -e "${CYAN}[INFO]${RESET} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${RESET} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${RESET} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${RESET} $1"
}

echo -e "${BOLD}${CYAN}"
echo "=========================================================="
echo "   🤖 AGENTIC WORKSPACE & ACADEMIC STARTER KIT SETUP     "
echo "   Powered by OMP, Google Antigravity & Obsidian Vault    "
echo "=========================================================="
echo -e "${RESET}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_VAULT="${HOME}/Documents/Academic-Vault"

# 1. Pastikan direktori dasar pengguna ada
log_info "Menyiapkan struktur direktori di ${HOME}..."
mkdir -p "${HOME}/.local/bin"
mkdir -p "${HOME}/.omp/agent/skills"
mkdir -p "${HOME}/.claude/skills"
mkdir -p "${HOME}/.agents/skills"
mkdir -p "${HOME}/Documents"

# 2. Pastikan ~/.local/bin masuk ke dalam PATH
export PATH="${HOME}/.local/bin:${PATH}"
SHELL_RC=""
if [ -n "${ZSH_VERSION}" ] || [ -f "${HOME}/.zshrc" ]; then
    SHELL_RC="${HOME}/.zshrc"
elif [ -f "${HOME}/.bashrc" ]; then
    SHELL_RC="${HOME}/.bashrc"
fi

if [ -n "${SHELL_RC}" ] && ! grep -q ".local/bin" "${SHELL_RC}"; then
    echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> "${SHELL_RC}"
    log_success "Direktori ~/.local/bin ditambahkan ke ${SHELL_RC}"
fi

# 3. Instalasi atau verifikasi biner OMP (Oh-My-Pi)
if command -v omp &> /dev/null; then
    log_success "OMP sudah terpasang: $(omp --version 2>/dev/null || echo 'installed')"
else
    log_info "Memasang versi terbaik OMP..."
    curl -fsSL https://raw.githubusercontent.com/can1357/oh-my-pi/main/install.sh | bash || true
fi

# 4. Pasang konfigurasi OMP & model Google Antigravity / 9Router
log_info "Memasang konfigurasi OMP & model terkurasi..."
mkdir -p "${HOME}/.omp/agent"
cp "${SCRIPT_DIR}/config/omp/config.yml" "${HOME}/.omp/agent/config.yml"
cp "${SCRIPT_DIR}/config/omp/models.yml" "${HOME}/.omp/agent/models.yml"

# Pasang pedoman AGENTS.md dan CLAUDE.md
if [ -f "${SCRIPT_DIR}/config/AGENTS.md" ]; then
    cp "${SCRIPT_DIR}/config/AGENTS.md" "${HOME}/.omp/agent/AGENTS.md"
    cp "${SCRIPT_DIR}/config/AGENTS.md" "${HOME}/.claude/CLAUDE.md"
fi
log_success "Konfigurasi OMP, models.yml, dan AGENTS.md berhasil disinkronkan."

# 5. Salin seluruh Skills kurasi
log_info "Menyinkronkan skills akademik dan software engineering..."
SKILL_COUNT=0
if [ -d "${SCRIPT_DIR}/skills" ]; then
    for skill_dir in "${SCRIPT_DIR}/skills/"*/*; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            for dest in "${HOME}/.agents/skills" "${HOME}/.omp/agent/skills" "${HOME}/.claude/skills"; do
                mkdir -p "$dest/$skill_name"
                cp -R "$skill_dir/"* "$dest/$skill_name/" 2>/dev/null || true
            done
            SKILL_COUNT=$((SKILL_COUNT + 1))
        fi
    done
fi
log_success "Berhasil memasang ${SKILL_COUNT} skills terkurasi ke direktori agent."

# 6. Pasang Template Obsidian Academic Vault
if [ -d "${TARGET_VAULT}" ]; then
    log_warn "Vault Obsidian sudah ada di: ${TARGET_VAULT}. Melewati penimpaan file naskah."
else
    log_info "Memasang Template Obsidian Academic Vault ke: ${TARGET_VAULT}..."
    if [ -d "${SCRIPT_DIR}/vault-template" ]; then
        cp -R "${SCRIPT_DIR}/vault-template" "${TARGET_VAULT}"
        log_success "Vault Obsidian berhasil dipasang di ${TARGET_VAULT}."
    fi
fi

# 7. Verifikasi Companion Tools
log_info "Memeriksa ketersediaan companion tools..."
for tool in uv typst pandoc git; do
    if command -v "$tool" &> /dev/null; then
        log_success "$tool terdeteksi."
    else
        log_warn "$tool belum terpasang (opsional)."
    fi
done

# 8. Login Google Antigravity (Otomatis & Resmi)
echo ""
echo -e "${BOLD}--- LOGIN GOOGLE ANTIGRAVITY ---${RESET}"
echo "Menggunakan autentikasi resmi Google Antigravity dan model gratis 9Router."
read -r -p "Apakah Anda ingin login ke Google Antigravity sekarang? (Y/n): " login_ag_choice
if [[ "${login_ag_choice}" =~ ^[Nn]$ ]]; then
    log_info "Login dilewati. Anda dapat login kapan saja dengan perintah: omp login google-antigravity"
else
    if command -v omp &> /dev/null; then
        omp login google-antigravity || log_warn "Login dapat diselesaikan nanti via perintah: omp login google-antigravity"
    else
        log_warn "OMP biner belum ditemukan di PATH saat ini."
    fi
fi

echo ""
echo -e "${BOLD}${GREEN}==========================================================${RESET}"
echo -e "${BOLD}${GREEN}   ✅ SETUP SELESAI & SISTEM SIAP DIGUNAKAN!              ${RESET}"
echo -e "${BOLD}${GREEN}==========================================================${RESET}"
echo ""
echo "Cara Menggunakan:"
echo "1. Buka folder proyek atau skripsi Anda:"
echo -e "   ${CYAN}cd ${TARGET_VAULT}${RESET}"
echo "2. Jalankan OMP di terminal:"
echo -e "   ${CYAN}omp${RESET}"
echo "3. Buka aplikasi Obsidian dan pilih 'Open folder as vault' mengarah ke:"
echo -e "   ${CYAN}${TARGET_VAULT}${RESET}"
echo ""
