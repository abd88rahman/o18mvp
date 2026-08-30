Skenario Data Testing - Distributor Ban (Nov 2024 - Feb 2026)
=============================================================

Status: **file induk/spec, direview user (2026-08-27).** Detail
transaksi (tanggal, nominal per baris) ada di
01-transaksi-distributor-ban.md,
cara eksekusinya di UI ada di
02-prosedur-testing.md — dokumen ini jadi
rujukan asumsi/parameter supaya tidak perlu diulang di tiap baris
transaksi.

Tujuan: dataset testing multi-tahun yang realistis buat menguji
``c18_basic_erp`` (khususnya FIFO costing, amortisasi manual via Jurnal
Umum, Tutup Buku dengan volume transaksi wajar) — dipakai bareng
c18_basic_erp-prosedur-testing.md,
bukan pengganti.

A. Profil Perusahaan
--------------------

-  Nama: **PT Roda Sejahtera** (distributor ban mobil, jual ke
   reseller).
-  Berdiri: **November 2024**.
-  Karyawan: 2 orang — **Si A** (gaji = UMR berjalan), **Si B** (gaji =
   UMR berjalan × 110%).

B. Gaji per Tahun
-----------------

Riset UMP DKI Jakarta (2026-08-27):

+-------+-----------------+-----------+------------------+
| Tahun | UMP DKI Jakarta | Gaji Si A | Gaji Si B (+10%) |
+=======+=================+===========+==================+
| 2024  | 5.067.381       | 5.067.381 | 5.574.119        |
+-------+-----------------+-----------+------------------+
| 2025  | 5.396.791       | 5.396.791 | 5.936.470        |
+-------+-----------------+-----------+------------------+
| 2026  | 5.729.876       | 5.729.876 | 6.302.864        |
+-------+-----------------+-----------+------------------+

Sumber:
`hukumonline.com <https://www.hukumonline.com/berita/a/ump-dan-umsp%E2%80%93dki-2026-lt697324d20263d/>`__,
`antaranews.com <https://www.antaranews.com/berita/5320501/ump-jakarta-2026-ditetapkan-sebesar-rp57-juta>`__,
`jakarta.nu.or.id <https://jakarta.nu.or.id/jakarta-raya/pemprov-dki-tetapkan-ump-jakarta-2026-rp5-72-juta-naik-6-17-persen-RHwlv>`__.
UMP 2026 naik 6,17%, berlaku efektif 1 Januari 2026.

Nominal di file transaksi detail nanti dibulatkan ke ribuan terdekat.

C. Timeline Setup Awal (November-Desember 2024)
-----------------------------------------------

1. **Modal saham awal** — Rp 1.000.000.000, masuk ke **Bank**, November
   2024.
2. **Sewa kantor tahunan** — dibayar lunas di muka, 1 tahun (Nov
   2024-Okt 2025). **Asumsi nominal: Rp 120.000.000/tahun (Rp
   10.000.000/bulan)**. Masuk akun “Biaya Dibayar Dimuka” (1-1420),
   diamortisasi ke akun **“6-1600 Beban Sewa”** (akun baru, lihat poin
   H) tiap bulan. Per 31 Des 2024: sudah 2 bulan lewat (Nov+Des) → sisa
   “Sewa Dibayar Dimuka” = 10 bulan × 10jt = **Rp 100.000.000**.
3. **Perabotan kantor (jadi Aset Tetap)** — meja, kursi, lemari, 2
   laptop (buat 2 karyawan), printer. **Asumsi total Rp 31.400.000**,
   masuk “Peralatan Kantor” (1-2300).
4. **ATK & barang habis pakai** — kertas, pulpen, papan tulis, dll.
   **Asumsi Rp 2.500.000** (stok awal kantor), langsung jadi Beban
   (6-1100), bukan aset.
5. **Pembelian persediaan pertama — 20 November 2024.**
6. **Penjualan pertama ke reseller — 17 Desember 2024.**

D. Master Produk - 9 SKU Ban
----------------------------

+--------+---------------+----------------------------+------------+
| Kode   | Merk/Tipe     | Harga Beli Awal (Nov 2024) | Harga Jual |
+========+===============+============================+============+
| BAN-A1 | Merk A Tipe 1 | 700.000                    | 850.000    |
+--------+---------------+----------------------------+------------+
| BAN-A2 | Merk A Tipe 2 | 750.000                    | 900.000    |
+--------+---------------+----------------------------+------------+
| BAN-A3 | Merk A Tipe 3 | 800.000                    | 950.000    |
+--------+---------------+----------------------------+------------+
| BAN-B1 | Merk B Tipe 1 | 650.000                    | 800.000    |
+--------+---------------+----------------------------+------------+
| BAN-B2 | Merk B Tipe 2 | 700.000                    | 850.000    |
+--------+---------------+----------------------------+------------+
| BAN-B3 | Merk B Tipe 3 | 720.000                    | 870.000    |
+--------+---------------+----------------------------+------------+
| BAN-B4 | Merk B Tipe 4 | 780.000                    | 930.000    |
+--------+---------------+----------------------------+------------+
| BAN-C1 | Merk C Tipe 1 | 900.000                    | 1.080.000  |
+--------+---------------+----------------------------+------------+
| BAN-C2 | Merk C Tipe 2 | 950.000                    | 1.140.000  |
+--------+---------------+----------------------------+------------+

Harga beli naik bertahap tiap beberapa bulan di 2025 (ditentukan bebas
saat nulis file transaksi detail) — supaya kelihatan efek FIFO (layer
harga beda-beda), tapi tidak setiap SKU naik bulan yang sama (lebih
realistis).

E. Pola Transaksi 2025
----------------------

-  **Minimal 1x pembelian & 2x penjualan per bulan** (Jan-Des 2025).
-  **Amortisasi sewa kantor**: jalan tiap bulan Jan-Okt 2025 (10 bulan,
   melunasi sisa Sewa Dibayar Dimuka dari poin C.2). **Sewa tahun
   kedua** dibayar Nov 2025 untuk periode Nov 2025-Okt 2026 — supaya
   amortisasi tetap jalan sampai cakupan skenario (Feb 2026), konsisten
   dengan pola “sewa tahunan”.
-  **Biaya operasional bulanan lain**: listrik & internet (asumsi flat
   Rp 1.500.000 listrik + Rp 500.000 internet/bulan, naik dikit di
   2026), gaji 2 karyawan (sesuai tabel B).
-  **Persediaan**: FIFO, pencatatan **Perpetual**
   (``costing_method = fifo``, sudah sesuai default konvensi Basic).

F. Skenario Kas/Bank
--------------------

-  Modal & transaksi besar (sewa, perabotan, pembelian persediaan ke
   vendor) → **Bank**.
-  ATK, biaya kecil (listrik, internet) → **Kas** (kadang Bank,
   divariasikan).
-  Gaji karyawan → **Bank** (transfer).
-  Penerimaan dari penjualan → campuran **Kas & Bank** (simulasi
   sebagian reseller bayar tunai, sebagian transfer) + 1-2 kali
   **Piutang belum lunas** dulu (biar kelihatan proses Penerimaan
   Piutang juga).
-  1x **Transfer Kas↔Bank** buat variasi.

G. Cakupan Waktu
----------------

-  **Nov 2024 - Des 2024**: setup awal + pembelian pertama + penjualan
   pertama + amortisasi sewa 2 bulan + gaji Nov & Des. Ditutup dengan
   **Tutup Buku Fiscal Year 2024** (langsung, tidak ditunda).
-  **Jan - Des 2025**: pola bulanan (1+ pembelian, 2+ penjualan, sewa
   amortisasi 10 bulan sampai Okt, sewa tahun ke-2 mulai Nov,
   listrik/internet/gaji tiap bulan). **Tutup Buku Fiscal Year 2025
   SENGAJA DITUNDA** (ditambah 2026-08-30) — tidak langsung diproses di
   akhir Des 2025, baru diproses setelah transaksi Feb 2026 berjalan
   (lihat detail & alasan di poin bawah).
-  **Jan - Feb 2026**: lanjutan pola yang sama, 2 bulan saja, **dengan
   buku 2025 masih terbuka** (belum ditutup) selama periode ini.

Kenapa Tutup Buku 2025 Ditunda (ditambah 2026-08-30)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tujuannya buat mengamati efek akun **“3-1100 Laba Ditahan”** sebelum vs
sesudah proses Tutup Buku — hal yang tidak kelihatan kalau Tutup Buku
langsung diproses begitu tahunnya selesai (pola yang dipakai untuk
2024). Urutannya: transaksi Jan 2026 jalan dulu → cek saldo Laba Ditahan
(harusnya masih cuma refleksi hasil 2024, belum termasuk 2025) →
transaksi Feb 2026 jalan → baru proses Tutup Buku Fiscal Year 2025 → cek
lagi saldo Laba Ditahan (sekarang harus berubah sebesar hasil bersih
2025). Detail checkpoint & langkah lengkap ada di
01-transaksi-distributor-ban.md
(akhir Januari & akhir Februari 2026) dan
02-prosedur-testing.md poin 7-7b.

Aman secara sistem — penguncian periode cuma memblokir tanggal ≤ tanggal
Tutup Buku terakhir yang sudah posted, jadi menunda Tutup Buku 2025
tidak menghalangi input transaksi 2026. - **Maret 2026** (ditambah
2026-08-28): batch transaksi khusus buat menutup gap coverage fitur yang
belum pernah dilewati skenario reguler (lihat poin H & I) — Uang Muka
Pembelian/Penjualan, Retur Barang Vendor, Write-off Hutang, Pemakaian
Sendiri, Stok Opname, 4 jenis Aktiva Tetap sisanya, Payroll pembayaran
sebagian.

H. Cost Center (ditambah 2026-08-28)
------------------------------------

2 Cost Center dibuat sebagai master data, dipakai buat nge-tag transaksi
batch Maret 2026 (poin G) — retrofit ringan, transaksi bulan-bulan
sebelumnya (Nov 2024-Feb 2026) **tidak perlu diubah/ditag ulang**, cukup
dibiarkan kosong seperti aslinya:

-  **Operasional** — buat tag Payroll, Kas Keluar operasional, dan
   sejenisnya.
-  **Gudang** — buat tag Pemakaian Sendiri, Stok Opname, dan aktivitas
   terkait persediaan fisik.

I. Keterbatasan yang Ditemukan (Multi-Currency)
-----------------------------------------------

Field ``currency_id``/``exchange_rate`` di ``c18.account.move`` ada,
tapi **mesin akuntansinya belum melakukan konversi otomatis ke mata uang
company** saat agregasi (Trial Balance, Tutup Buku) — kalau ada 1 jurnal
dalam USD sementara semua lainnya IDR, perhitungan saldo/tutup buku
bakal salah baca nilainya (dianggap seolah-olah sama-sama IDR).
**Sengaja TIDAK dites** di skenario ini supaya tidak merusak angka
checkpoint — ini dicatat sebagai temuan gap implementasi, bukan sesuatu
yang perlu “disiasati” lewat data testing. Perbaikan kodenya di luar
scope dokumen testing ini.

Status Kelengkapan
------------------

-  [x] Detail tanggal & nominal per baris transaksi —
   01-transaksi-distributor-ban.md.
-  [x] Nama-nama reseller/vendor spesifik — 1 vendor (PT Ban Nusantara
   Distribusi), 4 customer (Toko Ban Makmur, UD Roda Mas, Bengkel Sinar
   Jaya, Toko Onderdil Abadi), lihat 01.
-  [x] Skema kenaikan harga beli per SKU per bulan — lihat tabel “Skema
   Kenaikan Harga Beli” di 01.
-  [x] Prosedur eksekusi di UI —
   02-prosedur-testing.md.
-  [x] Gap coverage fitur (Uang Muka, Retur Vendor, Write-off Hutang,
   Pemakaian Sendiri, Stok Opname, Aktiva Tetap 4 jenis sisanya, Payroll
   partial) — batch Maret 2026, lihat poin G.
-  [ ] Belum pernah dijalankan tester sungguhan ke instance Odoo.
