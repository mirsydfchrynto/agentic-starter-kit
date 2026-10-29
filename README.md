# 🤖 Agentic Workspace & Academic Starter Kit

Starter kit lingkungan kerja AI Agent berbasis terminal (**OMP / Oh-My-Pi**) yang terintegrasi langsung dengan **Google Gemini Pro / Flash**, **Obsidian Knowledge Vault**, dan puluhan **Agent Skills** terkurasi untuk rekayasa perangkat lunak dan penulisan skripsi/tugas akhir harian.

Dirancang agar siap di-*clone* dan langsung berjalan dalam 1 perintah tanpa membawa riwayat sesi atau data pribadi pengembang sebelumnya.

---

## ⚡ Fitur Utama

- **Tier Terbaik Google Antigravity & Gemini:** Menggunakan konfigurasi model penalaran tertinggi: `google-antigravity/gemini-4-argon:high` untuk Task & Coding Sub-agents, dan `google-antigravity/gemini-3.8-flash:high` untuk Default/Plan/Vision/Judge, dengan fallback otomatis ke `gemini-2.5-pro` dan `gemini-2.5-flash`.
- **Automated 1-Step Setup:** Skrip `setup.sh` otomatis memasang biner `omp`, menyinkronkan seluruh konfigurasi model, mendaftarkan puluhan skill, dan menyiapkan Obsidian Academic Vault.
- **Obsidian Academic Vault Siap Pakai:** Struktur folder riset formal (`00-Inbox`, `10-Skripsi/Bab-1-5`, `20-Projects`, `30-Knowledge`, `40-Debug-TIL`, `50-Agent-Memory`) dilengkapi diagram visual `Skripsi-Workflow.canvas`.
- **Aturan Kritis Anti-Slop & Anti-Yes-Man:** Mengintegrasikan protokol penulisan lugas tanpa basa-basi (*no AI slop*), evaluasi asumsi kritis sebelum menyetujui ide, dan prinsip minimalisme kode (*Ponytail Protocol*).
- **Curated Skills Suite:**
  - **Akademik & Skripsi:** `proposal-skripsi`, `skripsi-auditor`, `sinta-scholar-search` (SINTA 1 & 2 / Garuda), `arxiv`, `grounded-citations`, `docx`, `pdf`, `powerpoint`, `humanizer`, `no-ai-slop`, `json-canvas`, `obsidian-markdown`.
  - **Rekayasa Perangkat Lunak:** `tdd`, `diagnosing-bugs`, `domain-modeling`, `code-review`, `code-simplifier`, `safe-change`, `security-audit`, `ui-ux-pro-max`, `github`, `ponytail-review`.

---

## 📋 Prasyarat Sistem

1. Sistem Operasi: Windows 10/11 (PowerShell), Linux (Ubuntu, Debian, Arch, Fedora), macOS, atau Windows WSL2.
2. Shell: PowerShell (Windows) atau Bash/Zsh (Linux/macOS).
3. Alat Dasar: `git` (sudah terpasang).
4. Akun Google Gemini: [Google AI Studio API Key](https://aistudio.google.com/app/apikey).

---

## 🚀 Panduan Instalasi Cepat

### Untuk Pengguna Windows (PowerShell)
Buka **PowerShell** (Run as Administrator tidak wajib), lalu jalankan:
```powershell
# 1. Clone repository
git clone https://github.com/mirsydfchrynto/agentic-starter-kit.git
cd agentic-starter-kit

# 2. Jalankan instalasi native Windows (pilih salah satu)
powershell -ExecutionPolicy Bypass -File .\setup.ps1
# ATAU:
.\setup.bat
```

### Untuk Pengguna Linux / macOS / WSL2
Buka terminal **Bash / Zsh**, lalu jalankan:
```bash
# 1. Clone repository
git clone https://github.com/mirsydfchrynto/agentic-starter-kit.git
cd agentic-starter-kit

# 2. Jalankan instalasi otomatis
chmod +x setup.sh
./setup.sh
```

Skrip akan meminta `GEMINI_API_KEY` jika belum disetel di sistem Anda. Masukkan API key Anda saat diminta.

---

## 📂 Struktur Repositori

```text
agentic-starter-kit/
├── config/
│   ├── AGENTS.md             # Instruksi sistem: No-AI-Slop, Critical Thinking, Ponytail
│   └── omp/
│       ├── config.yml        # Konfigurasi model roles, browser headless, tools
│       └── models.yml        # Definisi model Google Gemini Pro & Flash
├── skills/
│   ├── academic/             # Skill riset, sitasi, canvas, dan naskah skripsi
│   └── engineering/          # Skill TDD, debugging, code review, UI/UX
├── vault-template/           # Template Obsidian Academic Vault lengkap
├── env.example               # Contoh konfigurasi environment variable
├── setup.sh                  # Skrip instalasi otomatis untuk Linux/macOS
├── setup.ps1                 # Skrip instalasi native Windows (PowerShell)
└── README.md
```

---

## 🛠️ Cara Penggunaan Harian

### 1. Pengembangan Perangkat Lunak (Coding)
Buka terminal di dalam direktori proyek kode Anda dan ketik:
```bash
omp
```
Atau berikan prompt langsung:
```bash
omp "Desain skema basis data untuk sistem autentikasi menggunakan TDD"
```

### 2. Penulisan & Review Skripsi
Masuk ke direktori Obsidian Vault:
```bash
cd ~/Documents/Academic-Vault
omp
```
Cukup ketik dengan bahasa alami sehari-hari tanpa perlu menghafal atau mengetikkan nama skill. Agen secara otomatis mengenali tugas Anda dan langsung mengaktifkan skill terkait:
- *"Carikan 5 jurnal referensi tentang klasifikasi citra medis dan susun tabel State of the Art"* $\to$ Otomatis memicu `sinta-scholar-search` (filter minimal SINTA 2 / Scopus), `grounded-citations`, dan format telaah pustaka Bab 2.
- *"Bantu saya susun draf Bab 1 Pendahuluan tentang sistem antrean rumah sakit"* $\to$ Otomatis memicu `proposal-skripsi`, `skripsi-auditor`, dan `humanizer` tanpa gaya bahasa klise AI.
- *"Buat endpoint API login dan register di backend"* $\to$ Otomatis memicu `tdd` dan `ponytail` (kode ringkas, minim dependensi tambahan, teruji).
- *"Kenapa fungsi di baris 42 menghasilkan nilai undefined?"* $\to$ Otomatis memicu `diagnosing-bugs` dan `safe-change`.
### 3. Membuka di Aplikasi Obsidian
1. Buka aplikasi **Obsidian**.
2. Klik tombol **Open folder as vault**.
3. Pilih direktori: `~/Documents/Academic-Vault`.
4. Semua template Bab 1 - 5, Canvas alur skripsi, dan catatan siap digunakan.

---

## ⚙️ Penyesuaian Model & Kredensial

Jika Anda ingin mengganti API key di kemudian hari, buka file shell rc Anda (`~/.bashrc` atau `~/.zshrc`) dan perbarui:
```bash
export GEMINI_API_KEY="AIzaSy...KeyBaruAnda"
```
Lalu jalankan `source ~/.bashrc` atau `source ~/.zshrc`.

### Menggunakan Akun Google Antigravity (Gemini 3.8 / Gemini 4 / Claude Sonnet)
Jika Anda memiliki akun yang memiliki akses kuota **Google Antigravity**, Anda dapat menghubungkannya langsung ke OMP melalui OAuth browser:
```bash
omp login google-antigravity
```
Jendela browser akan terbuka otomatis untuk otentikasi akun Google Anda. Setelah login berhasil, seluruh model berikut langsung aktif:
- `google-antigravity/gemini-3.8-flash` (Vision + Fast Reasoning)
- `google-antigravity/gemini-4-argon` (Deep Analytical Architecture)
- `google-antigravity/claude-sonnet-5-5` (Coding & Heavy Analysis)
- `google-antigravity/claude-opus-5-5` (Deep Research & Complex Tasks)

Untuk menjalankan OMP langsung dengan model Antigravity:
```bash
omp --model google-antigravity/gemini-3.8-flash
```
Atau tekan `Ctrl+P` di dalam terminal OMP untuk mengganti model secara langsung.
