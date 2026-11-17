---
name: proposal-skripsi
description: >
  Panduan komprehensif dan pipeline otomasi untuk merancang, menyusun, memverifikasi,
  memformat DOCX/PDF, dan mengaudit Proposal Skripsi / Tugas Akhir (Bab 1-3 dan Bagian
  Awal/Akhir) pada empat skema (Proyek, Teknologi Tepat Guna / TTG, Produk Inovasi Lomba,
  Artikel Ilmiah). Wajib diaktifkan saat pengguna membuat draf proposal skripsi, menyusun
  latar belakang piramida terbalik, menyinkronkan rumusan masalah-tujuan-pengujian 1:1,
  membuat matriks literatur, memverifikasi DOI/Crossref/OJS & sitasi Zotero CSL IEEE [n],
  membersihkan pola AI-slop Bahasa Indonesia, membangun DOCX/PDF rapi berspasi 1.50 tepat,
  atau menyiapkan paket upload UTS dan versi bersih Turnitin tanpa lampiran mentah.
metadata:
  title: Arsitek & Auditor Proposal Skripsi Terapan (5 Fase)
  version: "2.0.0"
  author: mirsydfchrynto
---

# Proposal Skripsi v2.0.0 — Pipeline 5 Fase Terintegrasi

Gunakan skill ini sebagai orkestrator utama dari nol hingga naskah final siap kumpul (DOCX + PDF + paket bersih Turnitin). Setiap langkah memprioritaskan akurasi data primer, verifikasi pustaka langsung (*zero hallucinated citations*), tata bahasa Indonesia akademis alami, dan ketepatan tata letak OOXML.

---

## Peta Skema & Standar Cepat

Pilih salah satu dari **4 skema resmi** sebelum menulis satu paragraf pun (rincian struktur, rubrik 100 poin, dan daftar lampiran lihat [references/panduan_skema_dan_rubrik.md](references/panduan_skema_dan_rubrik.md)):

1. **Proyek**: Bab I–III inti + Subbab `3.5 Rencana Deployment` (+ bukti pengujian prototipe).
2. **Teknologi Tepat Guna (TTG)**: Bab I–III inti + Subbab `1.6 Profil Mitra` + Subbab `3.5 Rencana Penerapan & Serah Terima` (+ Surat Pernyataan Kesediaan Mitra).
3. **Produk Inovasi Lomba**: Bab I–III inti + Subbab `1.6 Profil Lomba` (+ bukti kepesertaan lomba & dokumentasi prototipe).
4. **Artikel Ilmiah**: **2 bab pendamping** (Bab I Pendahuluan <= 2 halaman + Bab II Rencana Publikasi target minimal SINTA 3 beserta jurnal cadangan) + Lampiran Draf Artikel siap submit & *supplementary files*.

---

## Alur Kerja Wajib 5 Fase

### Fase 1: Konsolidasi Data Primer, Keselarasan Logika & Pilihan Skema
Jangan mengarang angka masalah lapangan. Kumpulkan bukti primer terlebih dahulu (log transaksi POS/sistem, hasil wawancara bertanggal, observasi langsung, atau dokumen mitra).

1. Kunci **Matriks Keselarasan 1:1**:
   - **Rumusan Masalah (1.2)**: Wajib berbentuk pertanyaan terbuka (*Bagaimana...*, *Sejauh mana...*), dilarang pertanyaan Ya/Tidak.
   - **Tujuan Penelitian (1.3)**: Jumlah poin dan urutan identik 1:1 dengan Rumusan Masalah, diawali kata kerja operasional terukur (*Merancang*, *Mengimplementasikan*, *Menguji*, *Mengevaluasi*).
   - **Batasan Masalah (1.4)**: Dinyatakan sebagai **ruang lingkup** (pengguna, fitur, platform, dataset, periode), bukan kelemahan penelitian.
   - **Rencana Pengujian (3.4)**: Setiap poin Tujuan memetakan minimal satu indikator keberhasilan berpola **Metrik + Target Numerik + Kondisi/Skenario Uji**.
2. Jika berkolaborasi/ko-bimbingan pada topik atau domain berdekatan, rancang sudut pandang metode, variabel uji, dan struktur paragraf yang independen agar overlap n-gram lintas naskah tetap jauh di bawah `5%`.

### Fase 2: Pencarian Literatur & Verifikasi Bibliografi Nyata
Setiap sitasi wajib eksis secara nyata dan relevan dalam 5 tahun terakhir (minimal 10 jurnal untuk syarat dasar, target 25–35+ referensi primer agar sintesis Bab II kuat).

1. Gunakan skill pendamping untuk mengumpulkan sumber valid:
   - **`sinta-scholar-search`** untuk jurnal terakreditasi nasional SINTA 1–3, Garba Rujukan Digital (Garuda), dan Google Scholar.
   - **`arxiv` / `nature-citation` / `scientific-writing`** untuk literatur internasional ber-DOI dan standar penyusunan tinjauan pustaka berjenjang.
2. Simpan seluruh metadata sumber ke berkas BibTeX `daftar-pustaka.bib` dengan kunci berurutan `ref_01 .. ref_NN` sesuai urutan kemunculan perdana di naskah utama.
3. Verifikasi setiap DOI (via Crossref REST API + fallback OpenAlex) dan URL jurnal OJS non-DOI (`HTTP 200`), sekaligus pastikan kecocokan 1:1 dengan teks:
   ```bash
   uv run --with requests --with python-docx \
     scripts/verify_bib_crossref_ojs.py path/to/daftar-pustaka.bib --docx path/to/proposal.docx
   ```
   Perbaiki atau ganti entri apa pun yang berstatus `DOI_FAILED`, `URL_HTTP_4xx/5xx`, atau `missing_in_text`.

### Fase 3: Penulisan & Pembersihan Gaya Bahasa (Anti AI-Slop Indonesia)
Terapkan prinsip **`humanizer-indonesia`** dan **`no-ai-slop`** sebelum kompilasi akhir DOCX agar naskah lolos uji baca dosen pembimbing maupun metrik keseragaman kalimat (*burstiness*):

1. **Bab I.1 Piramida Terbalik**: Urutkan ketat `Konteks Makro -> Masalah Nyata Berbukti -> Solusi Terdahulu Bersitasi -> Kalimat Celah (Research Gap) -> Usulan Solusi`.
2. **Bab II.1 Sintesis Tematik + Tabel Pembanding**: Kelompokkan kajian berdasarkan pendekatan/metode, hindari pola daftar ringkasan ("Menurut X tahun Y..., Menurut A tahun B..."). Akhiri Bab II.1 dengan tabel perbandingan solusi sejenis yang menempatkan **Sistem Usulan pada kolom paling kanan**.
3. **Bab II.2 Uji Relevansi Teori**: Hanya muat teori yang benar-benar digunakan di Bab III, masing-masing memakai pola **Definisi -> Cara Kerja -> Relevansi Sistem**.
4. **Ritme Kalimat & Penghapusan AI-Tells**:
   - Hapus klise transisi robotik (*"Perlu dicatat bahwa"*, *"Bukan sekadar X melainkan Y"*, *"Di era digital saat ini"*, *"Dapat disimpulkan bahwa"*, *"holistik"*, *"komprehensif"*, *"signifikan"* berulang).
   - Variasikan panjang kalimat (campurkan kalimat pendek tegas 10–14 kata dengan kalimat analitis 22–32 kata; jaga rasio kalimat > 35 kata di bawah `15%` dan Koefisien Variasi panjang kalimat `CV >= 0.35`).
   - Pastikan **nol penulisan teknis bocor ke narasi** (jangan sertakan literal backtick `` ` ``, asterisk `**`, path file internal, ataupun nomor induk kependudukan / NIK 16-digit mentah).

### Fase 4: Pembangunan DOCX Interaktif & Rendering PDF Dua Pass
Hindari menyusun dokumen panjang langsung lewat klik manual Word yang rentan merusak spasi dan margin. Gunakan skrip pembangun Python berbasis `python-docx` yang mengimpor [scripts/docx_interactive_helpers.py](scripts/docx_interactive_helpers.py).

**Pagar Pengaman Teknis (*Why These Guardrails Exist*):**
- **Spasi Narasi `1.50` Tepat & Panjang Bab I–III `15–25` Halaman**: Pedoman akademik mewajibkan spasi `1.5` untuk keterbacaan dosen serta menjaga Bab I–III padat (tidak terlalu pendek dan tidak melebar menjadi bab laporan akhir).
- **Parser Markdown Inline Non-Rekursif (`add_rich_runs`)**: Regex splitter memecah `***...***`, `**...**`, `*...*`, `` `...` ``, `_{...}`, `^{...}` dan tautan sitasi Zotero `[n]` pada level tunggal. Jangan menulis tag bertingkat (`**teks *miring***`) dalam satu fragmen agar tidak meninggalkan karakter bintang literal di DOCX.
- **Konvergensi Halaman Daftar Isi 2-Pass (`extract_page_map`)**: LibreOffice tidak selalu me-refresh field nomor halaman TOC secara otomatis tanpa pemetaan awal. Bangun DOCX pass-1 -> render PDF via LibreOffice (`soffice --headless --convert-to pdf`) -> ekstrak halaman nyata menggunakan **jangkar heading/subbab awal halaman** (bukan substring teks yang bisa cocok di Daftar Isi) -> bangun ulang DOCX pass-2 sampai seluruh halaman Daftar Isi, Daftar Tabel, dan Daftar Gambar konvergen.
- **Section Break Romawi ke Arab**: Pisahkan Bagian Awal (`i, ii, iii...`, *Cover* tanpa nomor tampak) dan `BAB I` (`1, 2, 3...`) dengan *Section Break Next Page*, `is_linked_to_previous = False`, serta `configure_page_number_xml(section, fmt="decimal", start=1)`.
- **Diagram & Ilustrasi Vektor**: Bangun diagram Kerangka Pemikiran, Arsitektur Sistem, Flowchart/UML, dan Gantt dengan Matplotlib/Pillow beresolusi minimal `300 DPI` berpalet netral akademis dan sisipkan proporsional dengan `keep_with_next` pada caption.

### Fase 5: Audit Mutu, Uji Stilometri/Turnitin & Pengemasan Deliverables
Jalankan audit otomatis dan inspeksi visual sebelum menyerahkan berkas ke mahasiswa atau dosen:

1. **Audit Struktural, Gaya & Overlap** (opsional sertakan `--compare` jika membandingkan antar mahasiswa satu bimbingan, serta `--export-turnitin` untuk membuat versi bersih tanpa lampiran mentah):
   ```bash
   uv run --with python-docx --with pypdf --with numpy \
     scripts/audit_proposal_style.py path/to/proposal.docx \
     --pdf path/to/proposal.pdf \
     --export-turnitin path/to/UJI_TURNITIN_TANPA_LAMPIRAN/Proposal_Tanpa_Lampiran.pdf
   ```
   Untuk mengukur Perplexity Bahasa Indonesia luring memakai cache `cahya/gpt2-small-indonesian-522M` (selalu nonaktifkan progress bar agar output CLI tetap bersih):
   ```bash
   HF_HUB_DISABLE_PROGRESS_BARS=1 uv run --with python-docx --with pypdf --with numpy --with torch --with transformers \
     scripts/audit_proposal_style.py path/to/proposal.docx --perplexity
   ```
2. **Inspeksi Visual Halaman Kunci (`pdftoppm -png -r 140`)**: Render halaman Cover, Pengesahan, Daftar Isi, tabel panjang yang melewati batas halaman (`tblHeader`), halaman diagram, Daftar Pustaka, dan Lampiran Surat Mitra. Baca citra langsung untuk memverifikasi nol tabel terpotong, nol teks menumpuk watermark, dan konsistensi spasi.
3. **Review Kritis Pra-Kumpul**: Jalankan perspektif penguji menggunakan **`academic-paper-reviewer`** atau **`skripsi-auditor`** (jika relevan) terhadap rubrik 100 poin: Kelengkapan & Sistematika (20), Latar Belakang & Rumusan (25), Kajian & Kerangka (20), Metode & Indikator Uji (20), Tata Tulis, Sitasi & Similaritas (15).
4. **Pengemasan Bersih Penamaan Resmi**:
   - Berkas utama siap unggah (lengkap dengan lampiran): `UTS_<NIM>_<Nama_Lengkap>_<Skema>_<Kelas>.pdf` (sesuai ketentuan mata kuliah) plus sumber `.docx` & `.bib`.
   - Berkas opsional pratinjau Turnitin terpisah di subdirektori khusus tanpa lampiran mentah.

---

## Sinergi Ekosistem Skill Terpasang

| Tugas Spesifik | Skill Rujukan |
| :--- | :--- |
| Pencarian jurnal SINTA 1–3 & Garuda | `sinta-scholar-search` |
| Verifikasi metadata & sitasi berstandar riset | `nature-ref-verifier`, `nature-citation`, `grounded-citations` |
| Penataan struktur argumen ilmiah & ko-authoring | `scientific-writing`, `doc-coauthoring`, `academic-paper` |
| Eliminasi gaya bahasa robotik Indonesia | `humanizer-indonesia`, `no-ai-slop` |
| Simulasi review penguji ketat sebelum sidang | `academic-paper-reviewer`, `skripsi-auditor` |
| Manipulasi/inspeksi DOCX/PDF umum | `docx`, `pdf` |
