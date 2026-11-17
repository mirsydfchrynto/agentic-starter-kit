# Panduan 4 Skema, Tata Tulis, Rubrik Penilaian, dan Anti-Regresi Proposal Skripsi

Dokumen referensi ini merangkum aturan struktural, tata tulis, penilaian, serta pagar pengaman teknis (*anti-regression guardrails*) untuk keempat skema Proposal Tugas Akhir (Sarjana Terapan / S1 Teknik Informatika & Vokasi).

---

## 1. Perbandingan 4 Skema Tugas Akhir

| Skema | Struktur Proposal (UTS) | Struktur Laporan Akhir (UAS) | Lampiran Wajib Proposal | Lampiran Wajib Laporan Akhir |
| :--- | :--- | :--- | :--- | :--- |
| **Proyek** | Bab I–III inti + Subbab 3.5 **Rencana Deployment** | Bab I–V inti + Subbab 4.3 **Hasil Deployment** | Bukti pengujian prototipe awal; surat mitra (bila ada) + Matriks literatur | Bukti deploy (URL & tangkapan layar), bukti Hak Cipta, panduan pengguna |
| **Teknologi Tepat Guna (TTG)** | Bab I–III inti + Subbab 1.6 **Profil Mitra** + Subbab 3.5 **Rencana Penerapan & Serah Terima** | Bab I–V inti + Subbab 4.4 **Hasil Penerapan di Mitra** | **Surat Pernyataan Kesediaan Mitra** (bermaterai/resmi), dokumentasi prototipe + Matriks literatur | Berita acara serah terima produk, surat mitra, dokumentasi penerapan di lokasi mitra |
| **Produk Inovasi Lomba** | Bab I–III inti + Subbab 1.6 **Profil Lomba** | Bab I–V inti + Subbab 4.5 **Hasil Kompetisi** | Bukti kepesertaan/pendaftaran lomba, dokumentasi prototipe + Matriks literatur | Sertifikat juara (minimal juara 3 nasional/internasional, semester 5–8), surat pernyataan 1 produk 1 mahasiswa |
| **Artikel Ilmiah** | **2 Bab Pendamping**: Bab I Pendahuluan + Bab II Rencana Publikasi | **4 Bab Pembungkus**: Bab I Pendahuluan + Bab II Naskah Artikel + Bab III Proses Publikasi + Bab IV Penutup | **Draf artikel siap submit** sesuai templat jurnal tujuan (minimal **SINTA 3**), *supplementary files* (kode/dataset/instrumen) + Matriks literatur | Bukti terbit (URL/halaman jurnal), bukti peringkat minimal SINTA 3, *supplementary files*, korespondensi editor |

---

## 2. Anatomi & Standar Konten Bab I–III (Skema Proyek, TTG, Produk Inovasi Lomba)

### Bagian Awal (*Front Matter* — Penomoran Halaman Romawi Bawah Tengah `i, ii, iii...`)
1. **Halaman Judul (Cover)**: Tidak menampilkan nomor halaman (`i` tetap dihitung). Wajib mencantumkan nama skema di bawah judul (`Proposal Tugas Akhir - Skema ...`), logo resmi institusi, nama & NIM lengkap, program studi, fakultas, tahun.
2. **Halaman Persetujuan / Lembar Pengesahan**: Cantumkan dosen pembimbing / penilai sesuai ketentuan prodi. Gunakan tabel tanpa batas luar (*borderless*) untuk tata letak tanda tangan yang sejajar.
3. **Ringkasan Eksekutif (1 Paragraf Tunggal)**: Maksimal 250 kata, padat merangkum latar belakang masalah nyata, metode/teknologi solusi yang diusulkan, arsitektur sistem, serta target capaian terukur (tanpa kutipan pustaka atau sub-heading).
4. **Daftar Isi, Daftar Tabel, Daftar Gambar**: Dihasilkan otomatis dengan kode bidang Word (`TOC \o "1-3"`, `TOC \c "Tabel"`, `TOC \c "Gambar"`) sekaligus *internal hyperlink* ke bookmark setiap heading/caption agar navigasi klik langsung bekerja di MS Word, LibreOffice, maupun PDF viewer.

### Bab I Pendahuluan (Bobot 25 Poin)
- **1.1 Latar Belakang (Pola Piramida Terbalik Wajib)**:
  1. Konteks makro bidang kajian yang langsung relevan dengan topik.
  2. Masalah nyata di lapangan disertai **bukti empiris terverifikasi** (data transaksi, log error, hasil wawancara bertanggal, observasi lapangan). Dilarang mengarang angka.
  3. Tinjauan solusi terdahulu yang pernah ada (wajib bersitasi jurnal).
  4. **Kalimat celah penelitian (*research gap*)** yang menghubungkan kekurangan solusi terdahulu dengan kebutuhan kasus nyata.
  5. Usulan solusi sistem yang ditawarkan beserta kontribusinya.
- **1.2 Rumusan Masalah**: Berupa **pertanyaan terbuka** (*Bagaimana...*, *Sejauh mana...*), **dilarang** memakai pertanyaan tertutup (*Apakah...*).
- **1.3 Tujuan Penelitian**: Harus menggunakan **kata kerja operasional terukur** (*Merancang*, *Mengimplementasikan*, *Mengevaluasi*, *Menguji*), dengan **jumlah butir dan urutan berkorespondensi 1:1** terhadap Rumusan Masalah.
- **1.4 Batasan Masalah**: Dinyatakan sebagai **ruang lingkup sistem** (pengguna target, fitur utama, platform/perangkat, rentang atau jenis data, periode uji), **bukan** daftar kelemahan atau alasan keterbatasan mahasiswa.
- **1.5 Manfaat Penelitian**: Dipetakan eksplisit bagi setiap pihak pemangku kepentingan (mitra/pengguna, keilmuan/program studi, peneliti).
- **1.6 Subbab Khusus Skema**: *Profil Mitra* (untuk TTG: identitas usaha/komunitas, kondisi operasional saat ini dengan data primer, masalah utama yang dijawab) atau *Profil Lomba* (untuk Produk Inovasi Lomba: nama lomba, penyelenggara, tingkat, tahun, tahapan yang sudah ditempuh).

### Bab II Tinjauan Pustaka (Bobot 20 Poin)
- **2.1 Penelitian Terdahulu dan Solusi Sejenis**:
  - Disusun sebagai **sintesis tematik** (pengelompokan berdasarkan tema/pendekatan), **bukan daftar ringkasan artikel satu per satu** ("Penulis A melakukan..., Penulis B melakukan...").
  - Minimal **10 artikel ilmiah relevan** (target unggulan: 20–30+ referensi dengan >= 70% terbitan 5 tahun terakhir dan terakreditasi SINTA/Scopus/IEEE/DOI valid).
  - Ditutup dengan **Tabel Perbandingan Penelitian dan Solusi Sejenis** yang wajib menempatkan **Sistem Usulan pada kolom paling kanan** untuk memperlihatkan pembaruan fitur/metode secara visual.
- **2.2 Landasan Teori**:
  - Memuat **hanya** teori, algoritma, protokol, dan teknologi yang lolos uji relevansi (benar-benar dipakai dalam perancangan/implementasi Bab III).
  - Setiap teori mengikuti pola terstruktur: **Definisi Konseptual -> Cara Kerja/Mekanisme Teknis -> Relevansi langsung dengan Sistem Usulan**.
- **2.3 Kerangka Pemikiran**:
  - Disajikan dalam bentuk **1 diagram utuh** di akhir Bab II (alur *Masalah & Bukti -> Celah & Kebutuhan -> Pendekatan Metode -> Rencana Luaran/Pengujian*) beserta penjelasan naratif singkat.

### Bab III Metode Pelaksanaan (Bobot 20 Poin)
- **3.1 Tahapan Pengembangan**: Memilih model SDLC/penelitian (misalnya *Prototyping*, *Agile/Scrum*, *Waterfall*, atau *CRISP-DM* untuk AI/ML) lengkap dengan justifikasi akademis mengapa model cocok, diagram tahapan, dan daftar luaran konkrit tiap tahap.
- **3.2 Analisis Kebutuhan**: Kebutuhan fungsional (tabel kode `KF-01..KF-N` atau per aktor) dan kebutuhan non-fungsional (`KNF`: performa, keandalan, keamanan, kegunaan) yang diturunkan dari data mitra/observasi.
- **3.3 Perancangan Sistem**: Arsitektur sistem, pemodelan alur data/proses (DFD / UML Use Case / Activity / ERD), rancangan formulasi matematis/algoritma jika ada, serta antarmuka/spesifikasi perangkat keras jika relevan.
- **3.4 Rencana Pengujian**: Setiap butir tujuan pada 1.3 **wajib** memiliki kasus uji dengan indikator keberhasilan berpola **Metrik + Target Numerik + Kondisi/Skenario Uji** (misalnya: *Black-box pass rate 100% pada skenario X*, *RMSE <= Y pada dataset Z*, *SUS Score >= 75 dari N responden*).
- **3.5 Subbab Khusus Skema**: *Rencana Deployment* (Proyek) atau *Rencana Penerapan dan Serah Terima* (TTG: tahapan instalasi, pelatihan operator mitra, periode pendampingan, dan dokumen berita acara serah terima).
- **3.6 Jadwal Pelaksanaan**: Tabel Gantt terstruktur hingga pemenuhan kriteria akhir skema (mencakup penyiapan luaran wajib laporan akhir).

---

## 3. Format Teknis, Sitasi, & Aturan Turnitin

1. **Ukuran Kertas & Margin**:
   - Kertas **A4 Portrait (`21.0 x 29.7 cm`)**: Atas `4 cm`, Kiri `4 cm`, Bawah `3 cm`, Kanan `3 cm` (pola standar `4-4-3-3`).
   - Lampiran tabel/matriks lebar menggunakan Section break **A4 Landscape (`29.7 x 21.0 cm`)**: Kiri `3.5 cm`, Atas/Bawah/Kanan `3 cm`.
2. **Tipografi & Spasi Naskah Utama**:
   - Font: **Times New Roman 12 pt** untuk seluruh teks utama; `11 pt` nomor halaman; `9.5–10 pt` dalam tabel/keterangan gambar agar proporsional.
   - **Spasi baris narasi utama wajib `1.50` tepat** (`line_spacing = 1.5`), bukan `1.32` atau `1.15`, dan rata kiri-kanan (*Justify*) untuk paragraf isi.
   - **Panjang halaman Bab I–III**: Dikendalikan rapat di **15–25 halaman** (tidak terlalu tipis dan tidak membengkak melebihi batas wajar proposal).
3. **Referensi & Sitasi (IEEE Numerik / Zotero CSL)**:
   - Wajib menggunakan gaya tunggal secara konsisten (default direkomendasikan **IEEE `[1]`, `[2]`, ...**).
   - **Korepondensi 1:1 dan Urutan Naik**: Sitasi perdana di dalam teks harus muncul berurutan `[1], [2], [3], ...` tanpa nomor lompat, dan setiap nomor di daftar pustaka terpakai di teks utama.
   - **Kebenaran Bibliografi**: Dilarang mengarang DOI/judul/penulis. Setiap entri jurnal harus diverifikasi via API Crossref / OpenAlex atau URL OJS aktif (`HTTP 200`).
4. **Kebijakan AI, Plagiarisme, dan Berkas Bersih Turnitin**:
   - Proposal dengan tingkat kesamaan (*similarity*) **> 70%** atau terbukti plagiat mendapat nilai **0**.
   - Untuk uji Turnitin yang akurat sebelum pengumpulan, pisahkan lampiran mentah (misalnya transkrip mentah, kode penuh, surat bermeterai, atau tabel matriks penuh jika diminta terpisah) dan **dilarang** menyertakan Nomor Induk Kependudukan (NIK), nomor telepon pribadi, atau tanda tangan scan beresolusi penuh dalam repositori publik.

---

## 4. Pagar Pengaman Parser & Pipeline Otomasi (Anti-Regression Guardrails)

Setiap skrip pembangun dokumen (`build_*.py`) harus mematuhi aturan berikut agar hasil Word/PDF bebas bug struktural:

1. **Parser Markdown Inline Anti-Rekursi (`add_rich_runs`)**:
   - Jangan menyisipkan tag format bertingkat (*nested* seperti `**teks dengan `kode` atau *miring***` dalam satu blok); tulis secara berurutan atau pisahkan fragmennya agar tidak meninggalkan sisa artefak `*` atau `` ` `` di hasil render DOCX.
   - Jalankan audit otomatis pasca-build untuk memastikan **0 karakter backtick `` ` ``** dan **0 pasangan asterisk ganda `**`** tersisa di paragraf maupun sel tabel.
2. **Ekstraksi Nomor Halaman Daftar Isi (`extract_page_map`)**:
   - Pencocokan halaman judul di PDF untuk Bab I–III, Daftar Pustaka, dan Lampiran harus membaca **heading di awal halaman atau frasa unik subbab pertama** (`"1. pendahuluan" and "1.1 latar belakang"`), bukan sekadar substring nama bab yang bisa muncul di Daftar Isi atau paragraf biasa.
   - Lakukan iterasi kompilasi minimal 2 kali (`Build DOCX -> LibreOffice PDF -> Ekstrak Nomor Halaman PDF -> Rebuild DOCX`) sampai peta halaman Daftar Isi, Daftar Tabel, dan Daftar Gambar konvergen 100%.
3. **Penomoran Romawi-ke-Arab**:
   - Gunakan *Section Break Next Page* tepat sebelum Bab I dengan XML `<w:pgNumType w:fmt="decimal" w:start="1"/>` dan matikan `is_linked_to_previous` pada footer agar bagian awal tetap memakai `i, ii, iii...` sementara Bab I mulai tepat pada `1`.
4. **Penonaktifan Progress Bar HuggingFace saat Scoring Perplexity**:
   - Ketika menjalankan `cahya/gpt2-small-indonesian-522M` via `uv`, set `HF_HUB_DISABLE_PROGRESS_BARS=1` dan muat `local_files_only=True` bila model sudah tersedia di cache lokal.

---

## 5. Komponen Penilaian UTS Proposal (Total 100 Poin)

| No | Kriteria Penilaian | Bobot | Fokus Pemeriksaan Evaluator |
| :---: | :--- | :---: | :--- |
| 1 | Kelengkapan & Sistematika sesuai Skema + Lampiran | **20** | Ketepatan subbab skema, kelengkapan lampiran syarat skema, Daftar Isi/Tabel/Gambar akurat |
| 2 | Latar Belakang & Rumusan Masalah | **25** | Piramida terbalik berbasis data primer nyata, keselarasan 1:1 Rumusan Masalah -> Tujuan -> Batasan |
| 3 | Kajian Pustaka & Kerangka Pemikiran | **20** | Kedalaman sintesis tematik, tabel perbandingan berkolom Usulan di kanan, uji relevansi teori |
| 4 | Metode, Rencana Pengujian & Indikator | **20** | Keterkaitan model pengembangan dengan artefak rancangan, indikator uji pola Metrik + Target + Kondisi |
| 5 | Tata Tulis, Sitasi, & Similaritas | **15** | Spasi 1.5, margin A4, bahasa Indonesia baku alami (bebas AI slop), sitasi 1:1 terverifikasi, uji similaritas |
| | **Total** | **100** | |
