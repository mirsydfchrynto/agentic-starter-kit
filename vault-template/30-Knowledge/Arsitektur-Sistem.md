# 🏗️ Desain & Arsitektur Sistem

Dokumentasi rancangan teknis, diagram alir data (*data flow*), dan relasi antar komponen perangkat lunak.

## 1. Komponen Utama
- **Frontend / Client:** Antarmuka interaksi pengguna (PWA / Web / Mobile).
- **Backend / API:** Layanan pemrosesan bisnis dan kalkulasi algoritma.
- **Database:** Penyimpanan data transaksional dan riwayat pengujian.

## 2. Kontrak Data & Batas Akses
- Komunikasi menggunakan REST API / WebSocket.
- Validasi input di setiap batas modul untuk mencegah inkonsistensi data.
