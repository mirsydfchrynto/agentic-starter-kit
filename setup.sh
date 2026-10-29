#!/usr/bin/env bash
# ==============================================================================
# Agentic Workspace & Academic Starter Kit Setup Script
# Stack: OMP (Oh-My-Pi) + Google Gemini + Obsidian + Curated Agent Skills
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
echo "   Powered by OMP, Google Gemini & Obsidian Vault         "
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

if [ -n "${SHELL_RC}" ]; then
    if ! grep -q 'export PATH="${HOME}/.local/bin:${PATH}"' "${SHELL_RC}"; then
        echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> "${SHELL_RC}"
        log_info "Menambahkan ~/.local/bin ke PATH di ${SHELL_RC}"
    fi
fi

# 3. Instalasi atau verifikasi biner OMP (Oh-My-Pi)
if command -v omp &> /dev/null; then
    OMP_VERSION=$(omp --version 2>/dev/null || echo "terdeteksi")
    log_success "OMP sudah terpasang: ${OMP_VERSION}"
else
    log_info "Mengunduh dan memasang biner OMP via omp.sh..."
    if command -v curl &> /dev/null; then
        curl -fsSL https://omp.sh/install | sh
        log_success "Instalasi OMP selesai di ${HOME}/.local/bin/omp"
    else
        log_error "Perintah 'curl' tidak ditemukan. Harap pasang curl terlebih dahulu."
        exit 1
    fi
fi

# 4. Pasang konfigurasi OMP & model Gemini
log_info "Memasang konfigurasi OMP..."
if [ -f "${HOME}/.omp/agent/config.yml" ]; then
    cp "${HOME}/.omp/agent/config.yml" "${HOME}/.omp/agent/config.yml.bak"
    log_info "Backup config.yml lama disimpan ke config.yml.bak"
fi
cp "${SCRIPT_DIR}/config/omp/config.yml" "${HOME}/.omp/agent/config.yml"

if [ -f "${HOME}/.omp/agent/models.yml" ]; then
    cp "${HOME}/.omp/agent/models.yml" "${HOME}/.omp/agent/models.yml.bak"
    log_info "Backup models.yml lama disimpan ke models.yml.bak"
fi
cp "${SCRIPT_DIR}/config/omp/models.yml" "${HOME}/.omp/agent/models.yml"

# Pasang pedoman AGENTS.md dan CLAUDE.md
cp "${SCRIPT_DIR}/config/AGENTS.md" "${HOME}/.omp/agent/AGENTS.md"
cp "${SCRIPT_DIR}/config/AGENTS.md" "${HOME}/.claude/CLAUDE.md"
log_success "Konfigurasi OMP, models.yml, dan AGENTS.md berhasil disinkronkan."

# 5. Salin seluruh Skills kurasi
log_info "Menyinkronkan skills akademik dan software engineering..."
SKILL_COUNT=0

for skill_path in "${SCRIPT_DIR}/skills/academic"/* "${SCRIPT_DIR}/skills/engineering"/*; do
    if [ -d "${skill_path}" ]; then
        skill_name=$(basename "${skill_path}")
        cp -r "${skill_path}" "${HOME}/.agents/skills/"
        cp -r "${skill_path}" "${HOME}/.omp/agent/skills/"
        cp -r "${skill_path}" "${HOME}/.claude/skills/"
        SKILL_COUNT=$((SKILL_COUNT + 1))
    fi
done
log_success "Berhasil memasang ${SKILL_COUNT} skills terkurasi ke direktori agent."

# 6. Pasang Template Obsidian Academic Vault
if [ -d "${TARGET_VAULT}" ]; then
    log_warn "Vault Obsidian sudah ada di: ${TARGET_VAULT}"
    log_info "Melewati penimpaan file naskah untuk mencegah kehilangan data."
else
    log_info "Memasang Template Obsidian Academic Vault ke: ${TARGET_VAULT}..."
    cp -r "${SCRIPT_DIR}/vault-template" "${TARGET_VAULT}"
    log_success "Vault Obsidian berhasil dipasang di ${TARGET_VAULT}."
fi

# 7. Verifikasi Companion Tools (uv, typst, pandoc)
log_info "Memeriksa ketersediaan companion tools..."
if ! command -v uv &> /dev/null; then
    log_warn "uv (Python package runner) belum terpasang."
    log_info "Dapat dipasang otomatis dengan: curl -LsSf https://astral.sh/uv/install.sh | sh"
else
    log_success "uv terdeteksi: $(uv --version)"
fi

if ! command -v typst &> /dev/null; then
    log_warn "typst (kompiler dokumen ilmiah) belum terpasang."
    log_info "Dapat dipasang via package manager atau download dari: https://github.com/typst/typst"
else
    log_success "typst terdeteksi: $(typst --version)"
fi

if ! command -v pandoc &> /dev/null; then
    log_warn "pandoc (konverter naskah docx/pdf) belum terpasang."
else
    log_success "pandoc terdeteksi: $(pandoc --version | head -n 1)"
fi

# 8. Pemeriksaan GEMINI_API_KEY
echo ""
echo -e "${BOLD}--- PEMERIKSAAN KREDENSIAL API ---${RESET}"
if [ -z "${GEMINI_API_KEY}" ]; then
    log_warn "Variabel lingkungan GEMINI_API_KEY belum disetel!"
    echo "Untuk menggunakan Google Gemini di OMP, tambahkan baris berikut ke shell rc Anda (${SHELL_RC:-~/.bashrc}):"
    echo -e "${CYAN}export GEMINI_API_KEY=\"AIzaSy...IsiDenganKeyAnda\"${RESET}"
    echo ""
    read -r -p "Apakah Anda ingin memasukkan GEMINI_API_KEY sekarang? (y/N): " set_key_choice
    if [[ "${set_key_choice}" =~ ^[Yy]$ ]]; then
        read -r -p "Masukkan Gemini API Key: " user_api_key
        if [ -n "${user_api_key}" ]; then
            if [ -n "${SHELL_RC}" ]; then
                echo "export GEMINI_API_KEY=\"${user_api_key}\"" >> "${SHELL_RC}"
                export GEMINI_API_KEY="${user_api_key}"
                log_success "GEMINI_API_KEY berhasil disimpan ke ${SHELL_RC}."
            else
                export GEMINI_API_KEY="${user_api_key}"
                log_info "GEMINI_API_KEY aktif untuk sesi saat ini."
            fi
        fi
    fi
else
    log_success "GEMINI_API_KEY terdeteksi aktif di sistem."
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
