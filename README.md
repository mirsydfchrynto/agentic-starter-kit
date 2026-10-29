# 🤖 Agentic Workspace & Academic Starter Kit

Starter kit lingkungan kerja AI Agent berbasis terminal (**OMP / Oh-My-Pi**) yang terintegrasi langsung dengan **Google Gemini Pro / Flash**, **Obsidian Knowledge Vault**, dan puluhan **Agent Skills** terkurasi untuk rekayasa perangkat lunak dan penulisan skripsi/tugas akhir harian.

Dirancang agar siap di-*clone* dan langsung berjalan dalam 1 perintah tanpa membawa riwayat sesi atau data pribadi pengembang sebelumnya.

---

## ⚡ Fitur Utama

- **Zero-Config Google Gemini:** Menggunakan kuota API Google Gemini langsung (`gemini-2.5-pro` untuk reasoning & planning, `gemini-2.5-flash` untuk eksekusi cepat), tanpa memerlukan proxy lokal tambahan.
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

# 2. Jalankan instalasi native Windows
.\setup.ps1
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
Contoh prompt yang dapat langsung digunakan:
- *"Bantu saya susun Bab 1 Pendahuluan berdasarkan latar belakang masalah antrean di rumah sakit."*
- *"Audit Bab 3 Metodologi Penelitian di folder 10-Skripsi menggunakan mode skripsi-auditor."*
- *"Cari literatur di arXiv tentang federated learning untuk klasifikasi citra medis."*

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
