# Titik Akhir Sesi Ini (2026-08-28, sesi lanjutan)

## Kalimat Penutup Sesi
> (menunggu instruksi lanjutan dari user — sesi ini murni coding + testing `c18_basic_erp`, belum ada pertanyaan terbuka spesifik di akhir)

## Ringkasan Progres Sesi Ini
Sesi paling produktif sejauh ini — dari requirement lengkap (hasil sesi sebelumnya) sampai **modul jadi & lolos smoke test**.

1. **`c18_theme` dikonfirmasi user sudah smoke test** ke instance Odoo sungguhan, hasil sesuai ekspektasi (status di `erd/base/00-status-requirement.md` diupdate).
2. **Custom paper format A5H** ditambahkan ke `c18_theme` (`data/report_paperformat_a5h.xml`) — hasil diskusi soal ukuran kertas landscape vs orientasi fisik printer.
3. **Modul `c18_account` di-scaffold penuh, lalu di-rename jadi `c18_basic_erp`** (folder `app/mvp/c18_basic_erp/`) karena scope-nya jauh melebihi "accounting" — sekarang berisi **~35 model** mencakup SELURUH poin A-K dokumen `06-accounting-business.md`:
   - Fondasi: CoA (42 akun termasuk "6-1600 Beban Sewa" yang ditambah sesi ini), Journal (30 jenis + sequence), Account Move/Move Line, Cost Center, Exchange Rate.
   - Partner extend + Product tier Basic.
   - Kas Bank (Kas Masuk/Keluar/Transfer).
   - PO/SO ringan.
   - Siklus Pembelian **lengkap**: Penerimaan Barang, Pembelian (Vendor Bill, GRNI), Uang Muka Pembelian, Pembayaran Vendor (deduction), Retur Barang Vendor, Write-off Hutang.
   - Siklus Penjualan **lengkap** (mirror Pembelian) + costing FIFO/Average (`c18.account.stock.layer`).
   - Aktiva Tetap Basic (form generik 1 model, 5 jenis transaksi).
   - Payroll Basic (Pengakuan + Pembayaran, pull/push).
   - Persediaan: Pemakaian Sendiri, Stok Opname.
   - **Tutup Buku** (Penyesuaian Awal/Akhir Tahun dengan tanggal auto-locked, proses closing otomatis nolkan P&L ke Laba Ditahan, penguncian periode).
4. **Smoke test fungsional via `odoo shell`** — 7 skenario end-to-end, semua PASS (Jurnal Umum, PO→Pembelian, SO→Penjualan dengan FIFO costing benar, Stok Opname, Tutup Buku, penguncian periode). Dijalankan di database terpisah (`test_c18_basic_erp`), bukan database kerja, lalu di-rollback.
5. **Dataset testing realistis dibangun** — perusahaan fiktif "PT Roda Sejahtera" (distributor ban), 16+ bulan transaksi (Nov 2024-Apr 2026), 3 dokumen berjenjang di `testing/mvp/`:
   - `00-skenario-distributor-ban.md` — profil, gaji (riset UMP DKI Jakarta 2024/2025/2026), asumsi.
   - `01-transaksi-distributor-ban.md` — data transaksi kronologis lengkap + checkpoint stok/piutang-hutang.
   - `02-prosedur-testing.md` — cara eksekusi di UI, ditulis untuk tester tanpa background akuntansi.
   - Diperkaya 2 putaran: batch "Maret 2026" (Uang Muka, Retur Vendor, Write-off Hutang, Pemakaian Sendiri, Stok Opname, Aktiva Tetap 4 jenis sisanya, Payroll partial) + 7 transaksi penutup cakupan akun (Jaminan/Deposit, Pinjaman Bank+bunga, Leasing, Pendapatan Bunga, Beban Admin Bank/Denda) — cakupan akun sekarang 35/42 (83%).
6. **Modul `c18_help` (prototype)** — root menu "Help" top-level (setara Apps/Settings, sengaja tidak direparent ke `c18_theme.menu_erp_root`), nampilin 3 dokumen testing di atas sebagai form Odoo biasa (breadcrumb/sidebar tetap kelihatan) via field `Html` yang compute on-the-fly baca file `.rst` (docutils, bukan Markdown — `markdown` py package tidak ada di image `odoo:18`, `docutils` sudah ada). File `.rst` disalin manual dari `.md` sumber di `testing/mvp/` (bukan auto-convert).

## Temuan Gap (Dicatat, Belum Diperbaiki)
- **Multi-currency belum genuinely jalan**: field `currency_id`/`exchange_rate` ada di `c18.account.move`, tapi mesin akuntansinya (Trial Balance, Tutup Buku) belum konversi otomatis ke mata uang company saat agregasi. Kalau ada jurnal non-IDR, perhitungan saldo bakal salah. **Sengaja tidak dites** di skenario testing (dicatat di `00-skenario-distributor-ban.md` poin I) — perbaikan kode di luar scope sesi ini.

## Keputusan Besar yang Perlu Diingat
1. **`c18_common` resmi tidak dipakai** — sudah dikoreksi sesi sebelumnya, dikonfirmasi lagi sesi ini: Partner/Product Basic tetap bagian `c18_account`/`c18_basic_erp`.
2. **Rename `c18_account` → `c18_basic_erp`** (2026-08-27) — nama model Odoo (`c18.account.*`) TIDAK berubah, cuma technical module name. Dokumen historis (`erd/00-tiering-produk.md`, dll) sengaja dibiarkan pakai nama lama di narasi, cukup diberi catatan rename di bagian atas.
3. **Deduction Pembayaran Vendor/Penerimaan Piutang disederhanakan jadi level header** (bukan per-baris invoice + wizard popup) — efek jurnal tetap sama persis sesuai requirement, cuma UX-nya lebih simpel dari draft awal.
4. **CoA nambah 1 akun**: "6-1600 Beban Sewa" (Beban Usaha) — ditemukan lewat proses bikin skenario testing (sewa kantor numpang ke akun generik sebelumnya), dianggap layak jadi default karena hampir semua bisnis punya beban sewa.
5. **Testing procedure ditulis untuk tester non-akuntansi** — istilah awam, "Hasil yang Diharapkan" dalam bentuk observable (bukan istilah debit/kredit), checkpoint yang bisa dicocokkan tanpa hitung manual.

## Belum Dikerjakan / Masih Terbuka (Kandidat Sesi Berikutnya)
- [ ] **Jalankan skenario testing PT Roda Sejahtera secara manual di UI** (belum pernah dieksekusi tester sungguhan sama sekali — baru functional test via `odoo shell`).
- [ ] Perbaiki gap multi-currency (konversi otomatis ke company currency saat agregasi).
- [ ] Laporan Keuangan (Neraca/Laba Rugi/Trial Balance/Buku Besar) & Kartu Stok — belum ada modelnya sama sekali (tier Standard+, di luar scope Basic).
- [ ] Modul `c18_stock`/`c18_purchase`/`c18_sale` (Standard tier) — belum dibuat sama sekali, requirement-nya (`03-inventory-foundation.md`, `04-purchase.md`, `05-sales.md`) masih level tinggi.
- [ ] Riset 3 repo referensi payroll (`odoo18-toso`, `odoo18-cep`, `odoo10-kp3`) utk `07-hris.md` — **masih menggantung dari 2 sesi sebelumnya**.
- [ ] `c18_help` masih prototype — belum diputuskan jadi fitur permanen atau dibuang, belum ada requirement/PRD resmi.

## Peta Dokumen Penting
- `app/mvp/c18_basic_erp/` — modul kode utama, ~35 model, sudah smoke test functional.
- `testing/mvp/00-skenario-distributor-ban.md`, `01-transaksi-distributor-ban.md`, `02-prosedur-testing.md` — dataset & prosedur testing realistis, siap dieksekusi manual.
- `app/base/c18_help/` — prototype viewer dokumentasi (root menu "Help").
- `app/base/c18_theme/` — smoke test sudah confirmed, dianggap selesai.
- `erd/mvp/00-status-requirement.md` — status tracking utama, sudah diupdate mengikuti semua progres sesi ini.
