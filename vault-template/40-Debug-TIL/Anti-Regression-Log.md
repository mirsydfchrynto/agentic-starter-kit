# 🛑 Anti-Regression Log & Post-Mortem

Catatan rekayasa untuk mencegah pengulangan bug teknis, jebakan dependency, atau kegagalan konfigurasi sistem.

## Format Pencatatan:
1. **Gejala Masalah:** Pesan error dan perilaku yang teramati.
2. **Akar Penyebab (Root Cause):** Alasan teknis kegagalan.
3. **Solusi Baku:** Langkah perbaikan terverifikasi.
4. **Guardrail:** Aturan atau tes otomatis untuk mencegah regresi di masa depan.

---

### Contoh Catatan (Dapat Dihapus):
- **Gejala:** Koneksi database timeout saat migrasi skema tabel besar.
- **Akar Penyebab:** Lock eksklusif pada tabel aktif tanpa timeout transaksi.
- **Solusi Baku:** Tambahkan `SET lock_timeout = '5s';` sebelum eksekusi DDL.
