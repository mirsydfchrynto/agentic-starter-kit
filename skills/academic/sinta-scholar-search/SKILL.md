---
name: sinta-scholar-search
description: >
  Protocol and search guidelines for discovering, screening, and verifying accredited
  Indonesian national journals (SINTA 1 and SINTA 2) and international peer-reviewed papers
  via Garuda, Google Scholar, SINTA portal, and Crossref.
---

# SINTA 1 & 2 Literature Search & Verification Protocol

Gunakan skill ini ketika pengguna meminta pencarian literatur, jurnal referensi, atau penyusunan *State of the Art* Bab 2 dengan batas minimal **SINTA 2** atau reputasi internasional.

---

## 1. Ambang Batas Akreditasi (Quality Threshold)

- **Standar Minimal:** Jurnal Nasional Terakreditasi **SINTA 1** atau **SINTA 2** (SK Akreditasi Kemendikbudristek / Kemenristek-BRIN) atau Jurnal Internasional Bereputasi (Scopus Q1/Q2/Q3, WoS).
- **Larangan Keras:** Dilarang menggunakan prosiding tanpa peer-review, blog pribadi, makalah jurnal predator, atau jurnal SINTA 3–6 kecuali mendapat izin eksplisit pengguna.
- **Anti-Halusinasi Akreditasi:** Agen tidak boleh menebak peringkat SINTA. Status akreditasi wajib diverifikasi via portal resmi atau basis data ISSN.

---

## 2. Alur Pencarian Literatur Berdasarkan Judul / Topik

### Tahap 1: Ekstraksi Kata Kunci dari Judul
1. Pisahkan judul penelitian pengguna menjadi 3 komponen:
   - **Domain Permasalahan:** (contoh: *antrean kasir, reservasi barbershop, rekam medis*)
   - **Metode / Pendekatan:** (contoh: *Fuzzy Sugeno, Genetic Algorithm, Smart Dispatch, PWA*)
   - **Objek / Konteks Terapan:** (contoh: *UMKM, Retail, Rumah Sakit*)
2. Rumuskan variasi kata kunci dalam Bahasa Indonesia dan Bahasa Inggris untuk memperluas cakupan.

### Tahap 2: Basis Data Pencarian
1. **Garuda (Garba Rujukan Digital):** `https://garuda.kemdikbud.go.id/`
   - Indeks utama artikel ilmiah terakreditasi nasional.
2. **Portal SINTA Journals:** `https://sinta.kemdikbud.go.id/journals`
   - Gunakan filter kategori: `S1` atau `S2` pada rumpun ilmu informatika/komputer.
3. **Google Scholar:**
   - Gunakan kueri spesifik berparameter nama jurnal SINTA terverifikasi atau ISSN:
     ```text
     "kata kunci topik" site:ac.id filetype:pdf
     "kata kunci topik" source:"nama jurnal sinta 2"
     ```
4. **Daftar Jurnal Informatika / Ilmu Komputer SINTA 1 & 2 Populer:**
   - *RESTI (Rekayasa Sistem dan Teknologi Informasi)* - SINTA 1 / 2
   - *JOIV (International Journal on Informatics Visualization)* - SINTA 1 / Scopus
   - *JNTETI (Jurnal Nasional Teknik Elektro dan Teknologi Informasi)* - SINTA 2
   - *JUTI (Jurnal Ilmiah Teknologi Informasi)* - SINTA 2
   - *JEPIN (Jurnal Edukasi dan Penelitian Informatika)* - SINTA 2
   - *SISFO / Jurnal Sistem Informasi* - SINTA 2
   - *IJCCS (Indonesian Journal of Computing and Cybernetics Systems)* - SINTA 2

---

## 3. Protokol Verifikasi Bukti Sitasi

Setiap artikel yang direkomendasikan wajib mencantumkan data verifikasi lengkap:
1. **Judul Artikel:** [Judul lengkap persis]
2. **Penulis & Tahun:** [Nama penulis utama et al., Tahun terbit]
3. **Nama Jurnal:** [Nama lengkap jurnal penerbit]
4. **Akreditasi:** [SINTA 1 / SINTA 2 terkonfirmasi]
5. **ISSN / E-ISSN:** [Nomor identitas penerbitan]
6. **URL / DOI:** [Tautan resmi jurnal atau nomor DOI aktif]

---

## 4. Format Output State of the Art (Bab 2)

Sajikan hasil telaah literatur dalam format tabel komparatif berikut ke dalam draf Bab 2:

| No | Penulis & Tahun | Judul Penelitian | Nama Jurnal & Akreditasi | Metode yang Digunakan | Temuan Kunci / Kinerja | Kesenjangan (Research Gap) dengan Penelitian Ini |
|---|---|---|---|---|---|---|
| 1 | Pratama dkk. (2024) | Optimasi Antrean Pelayanan... | Jurnal RESTI (SINTA 2) | Algoritma Genetika | Menurunkan waktu tunggu 22% | Belum menangani penjadwalan dinamis berbasis peran |
| 2 | ... | ... | ... | ... | ... | ... |

Wajib menyertakan narasi sintesis di bawah tabel yang menjelaskan benang merah bagaimana penelitian pengguna menutup *research gap* tersebut.
