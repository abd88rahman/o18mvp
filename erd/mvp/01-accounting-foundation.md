# Requirement - Fondasi Accounting/GL (`c18_account`)

Status: **draft direview sebagian (2026-08-26), belum diimplementasikan.**

**Tier: Semua tier** (Basic/Standard/Enterprise) — lihat [erd/00-tiering-produk.md](../00-tiering-produk.md). Fondasi ini yang dipakai baik oleh form jurnal generic tier Basic maupun fitur lengkap tier Standard+, cuma UI-nya beda.

## Kenapa Ini Duluan
Sales, Purchase, Inventory, dan HRIS (lewat payroll) semuanya di ujungnya menghasilkan transaksi yang harus dibukukan jadi jurnal (invoice → piutang, pembelian → hutang, stock movement → valuasi persediaan, payroll → beban gaji). Tanpa fondasi Accounting siap duluan, modul lain tidak punya tempat konsisten buat menaruh hasil transaksinya. Pola ini mengikuti proyek referensi `aviat-odoo` (`c18_account` dibangun duluan, modul lain depends ke situ) dan sejalan dengan `notes/human-notes/master-plan.txt` yang bilang fitur ERP kita "akan lebih mirip repo `odoo18_accurate`" — GL sebagai hub pusat, modul lain jadi sub-ledger yang lapor ke situ.

Sesuai [erd/00-konvensi-teknis.md](../00-konvensi-teknis.md): **zero dependency** ke app `account` bawaan Odoo — model dibangun dari nol, bukan `_inherit`. Nama modul awal: `c18_account` — **di-rename jadi `c18_basic_erp` (2026-08-27)** setelah scope-nya berkembang jauh melebihi GL/Accounting (Purchase, Sales, Inventory, Payroll, Fixed Assets ikut masuk demi "Basic cukup 1 modul", lihat [00-tiering-produk.md](../00-tiering-produk.md)). Nama **model** Odoo (`c18.account.*`) tidak berubah, cuma technical module name-nya.

## Scope

### 1. Chart of Accounts — `c18.account.account`
Kode akun, nama, tipe.

- **Data isi CoA**: modul `c18_account` bawa **data default siap pakai** (template daftar akun), supaya company baru langsung dapat CoA standar tanpa setup dari kosong, tapi tetap bisa diedit/disesuaikan.
- **Tipe akun** (ala Accurate, 15 tipe): Kas Bank, Piutang Usaha, Persediaan, Aktiva Lancar Lainnya, Aktiva Tetap, Aktiva Lain, Hutang Usaha, Hutang Lancar Lainnya, Hutang Jangka Panjang, Ekuitas, Pendapatan, Beban Pokok Pendapatan, Beban Usaha, Pendapatan di Luar Usaha, Beban di Luar Usaha.
- **Default akun kelompok Ekuitas** (bagian dari data default CoA di atas): Modal, Laba Ditahan, Laba Tahun Berjalan, Dividen, Balancing Account.

### 2. Journal — `c18.account.journal`
Daftar tipe jurnal yang dibutuhkan (granular, ala Accurate — bukan cuma "Sales/Purchase/Cash/General" generik ala Odoo native):

- Jurnal Umum
- Jurnal Kas Masuk (selain piutang customer), Jurnal Kas Keluar (selain utang vendor), Jurnal Transfer antar Kas
- **Siklus Pembelian**: Penerimaan Barang, Pembelian, Uang Muka Pembelian, Pembayaran Vendor, Retur Barang Vendor, Write-off Hutang
- **Siklus Penjualan**: Pengiriman Barang, Penjualan, Uang Muka Penjualan, Penerimaan Piutang, Retur Barang Customer, Write-off Piutang
- **Aktiva Tetap**: Pengakuan, Penyusutan, Penghapusan, Penjualan, Revaluasi
- **Payroll**: Hutang Gaji, Bayar Gaji
- **Tutup Buku**: Penyesuaian (awal tahun & akhir tahun), Tutup Buku

Daftar ini belum final ("sisanya menyusul") — akan bertambah begitu modul terkait (Purchase, Sales, Aktiva Tetap, Payroll) mulai digarap detail.

### 3. Account Move / Move Line — `c18.account.move` + `c18.account.move.line`
Header+detail jurnal, harus balance (debit=kredit) sebelum posting.

**Generic reference (`res_model`/`res_id`)** di tiap move line — konvensi supaya tiap baris jurnal bisa ditelusuri balik ke dokumen sumber yang men-generate-nya (pola yang sama seperti konvensi teknis di `odoo18_accurate`; akan dipromosikan ke [erd/00-konvensi-teknis.md](../00-konvensi-teknis.md) begitu diimplementasikan & terverifikasi, biar konsisten dipakai modul lain juga).

### 4. Cost Center (Pengganti Account Analytic) — `c18.account.cost.center`
Field `cost_center_id` (Many2one) di level **move line** — dipakai untuk analisis data (mis. laporan laba rugi per cost center). Master data Cost Center bersifat fleksibel — bisa diisi nama departemen, atau nama project, tergantung kebutuhan; bukan struktur multi-dimensi kayak Analytic Plan Odoo.

### 5. Multi-Currency
Dibutuhkan dari awal (bukan ditunda). 2 bagian:
- **Kurs transaksi** — tiap jurnal/transaksi punya field nilai kurs yang berlaku saat transaksi itu terjadi (disimpan waktu itu juga, bukan dihitung ulang belakangan).
- **Kurs periodik** — tabel master kurs harian (`c18.account.exchange.rate` atau serupa) untuk menyatakan ulang nilai dalam mata uang asal di laporan (Neraca, Laba Rugi, dll) pada tanggal tertentu.

### 6. Periode Akuntansi (Fiscal Period)
Tidak pakai `account.fiscal.year` bawaan Odoo (zero dependency). **Tanpa field tambahan** di move line — deteksi periode murni dari tanggal transaksi tiap kali validasi (tidak ada `period_id` disimpan). Kalau tanggal transaksi jatuh di periode yang sudah ditutup, blokir tambah/edit/hapus jurnal di tanggal itu.

## Belum Diputuskan / Perlu Digali
- [x] Detail sub-kategori/turunan tiap 15 tipe akun — **dikonfirmasi 2026-08-26**, data default CoA per tipe:

**Kolom tambahan (2026-08-26)**: "Default Fitur?" — apakah akun ini di-hardcode/fixed dipakai otomatis oleh 1 jenis jurnal tertentu (bukan cuma salah satu opsi bebas pilih user). Kalau Ya, kolom "Fitur Pemakai" nunjuk jenis jurnal & poin-nya di [06-accounting-business.md](06-accounting-business.md).

**Skema kode akun** (draft saya, dikoreksi 2026-08-26 — segmen pertama = tipe akun ala Accurate: 1=Aktiva, 2=Kewajiban, 3=Ekuitas, 4=Pendapatan, 5=Beban Pokok Pendapatan, 6=Beban Usaha, 8=Pendapatan di Luar Usaha, 9=Beban di Luar Usaha (**tidak ada prefix 7**); segmen kedua = urutan dalam tipe, kelipatan 100). Tandai kalau mau diganti lagi.

| No | Kode & Nama Akun | Tipe Akun | Default Fitur? | Fitur Pemakai |
|---|---|---|---|---|
| 1 | 1-1000 Kas | Kas Bank | Tidak | — (bebas pilih user) |
| 2 | 1-1100 Bank | Kas Bank | Tidak | — (bebas pilih user) |
| 3 | 1-1200 Piutang Usaha | Piutang Usaha | **Ya** | Penjualan (E.2), Penerimaan Piutang (E.4), Retur Barang Customer (E.5), Write-off Piutang (E.6) |
| 4 | 1-1300 Persediaan Barang Dagang | Persediaan | **Ya** | Penerimaan Barang (D.1), Pengiriman Barang (E.1), Retur Barang Vendor (D.5), Retur Barang Customer (E.5), Pemakaian Sendiri (F.1), Stok Opname (F.2) |
| 5 | 1-1400 Uang Muka Pembelian | Aktiva Lancar Lainnya | **Ya** | Uang Muka Pembelian (D.3) |
| 6 | 1-1410 PPN Masukan | Aktiva Lancar Lainnya | Tidak | — (belum ada fitur PPN dirancang) |
| 7 | 1-1420 Biaya Dibayar Dimuka | Aktiva Lancar Lainnya | Tidak | — |
| 8 | 1-2000 Tanah | Aktiva Tetap | Tidak | — (Basic: user pilih manual per transaksi, poin G) |
| 9 | 1-2100 Bangunan | Aktiva Tetap | Tidak | — (Basic: user pilih manual per transaksi, poin G) |
| 10 | 1-2200 Kendaraan | Aktiva Tetap | Tidak | — (Basic: user pilih manual per transaksi, poin G) |
| 11 | 1-2300 Peralatan Kantor | Aktiva Tetap | Tidak | — (Basic: user pilih manual per transaksi, poin G) |
| 12 | 1-2900 Akumulasi Penyusutan (kontra) | Aktiva Tetap | Tidak *(Basic)* | Baru fixed otomatis mulai Standard (penyusutan otomatis) |
| 13 | 1-3000 Aktiva Lain-lain | Aktiva Lain | Tidak | — |
| 14 | 1-3100 Jaminan/Deposit | Aktiva Lain | Tidak | — |
| 15 | 2-1000 Hutang Usaha | Hutang Usaha | **Ya** | Pembelian (D.2), Pembayaran Vendor (D.4), Retur Barang Vendor (D.5), Write-off Hutang (D.6) |
| 16 | 2-1100 Hutang Belum Difaktur | Hutang Usaha | **Ya** | Penerimaan Barang (D.1), Pembelian (D.2, kondisional), Retur Barang Vendor (D.5, kondisional) |
| 17 | 2-1200 Uang Muka Penjualan | Hutang Lancar Lainnya | **Ya** | Uang Muka Penjualan (E.3) |
| 18 | 2-1300 Hutang Gaji | Hutang Lancar Lainnya | **Ya** | Payroll — Jurnal Pengakuan & Pembayaran (H) |
| 19 | 2-1400 PPN Keluaran | Hutang Lancar Lainnya | Tidak | — (belum ada fitur PPN dirancang) |
| 20 | 2-1500 Hutang Pajak | Hutang Lancar Lainnya | Tidak | — (belum ada fitur PPN dirancang) |
| 21 | 2-2000 Hutang Bank Jangka Panjang | Hutang Jangka Panjang | Tidak | — |
| 22 | 2-2100 Hutang Leasing | Hutang Jangka Panjang | Tidak | — |
| 23 | 3-1000 Modal | Ekuitas | Tidak | — (setup awal manual) |
| 24 | 3-1100 Laba Ditahan | Ekuitas | **Ya** | Tutup Buku (C) |
| 25 | 3-1200 Laba Tahun Berjalan | Ekuitas | **Ya** | Tutup Buku (C) — saldo berjalan real-time, ikut ter-nolkan pas closing |
| 26 | 3-1300 Dividen | Ekuitas | Tidak | — |
| 27 | 3-1900 Balancing Account | Ekuitas | Tidak | — (belum ada fitur spesifik) |
| 28 | 4-1000 Pendapatan Penjualan/Jasa | Pendapatan | Tidak | — (opsi umum, tapi kredit di Penjualan tetap bebas pilih user, E.2) |
| 29 | 4-1100 Retur & Potongan Penjualan (kontra) | Pendapatan | **Ya** | Retur Barang Customer (E.5) |
| 30 | 5-1000 Beban Pokok Penjualan/HPP | Beban Pokok Pendapatan | **Ya** | Pengiriman Barang (E.1), Penjualan langsung tanpa delivery (E.2), Retur Barang Customer (E.5) |
| 31 | 6-1000 Beban Gaji | Beban Usaha | **Ya** | Payroll — Jurnal Pengakuan (H) |
| 32 | 6-1100 Beban ATK | Beban Usaha | Tidak | — (opsi bebas di Pemakaian Sendiri, F.1) |
| 33 | 6-1200 Beban Operasional | Beban Usaha | Tidak | — (opsi bebas di Pemakaian Sendiri, F.1) |
| 34 | 6-1300 Beban Piutang Tak Tertagih | Beban Usaha | **Ya** | Write-off Piutang (E.6) |
| 35 | 6-1400 Beban Penyusutan | Beban Usaha | Tidak *(Basic)* | — (Basic: manual, poin G) |
| 36 | 6-1500 Selisih Persediaan | Beban Usaha | **Ya** | Stok Opname (F.2) |
| 37 | 8-1000 Pendapatan Lain-lain | Pendapatan di Luar Usaha | **Ya** | Write-off Hutang (D.6) |
| 38 | 8-1100 Pendapatan Bunga | Pendapatan di Luar Usaha | Tidak | — |
| 39 | 9-1000 Beban Bunga | Beban di Luar Usaha | Tidak | — (opsi bebas di deduction Pembayaran Vendor/Penerimaan Piutang, D.4/E.4) |
| 40 | 9-1100 Beban Admin Bank | Beban di Luar Usaha | Tidak | — (opsi bebas di deduction Pembayaran Vendor/Penerimaan Piutang, D.4/E.4) |
| 41 | 9-1200 Beban Denda | Beban di Luar Usaha | Tidak | — (opsi bebas di deduction Pembayaran Vendor/Penerimaan Piutang, D.4/E.4) |
| 42 | 6-1600 Beban Sewa | Beban Usaha | Tidak | — (ditambah 2026-08-28, temuan dari skenario testing PT Roda Sejahtera — sebelumnya amortisasi sewa numpang ke 6-1200 Beban Operasional, dianggap layak jadi akun default sendiri krn hampir semua bisnis punya beban sewa & nilainya material) |

Akun yang sudah punya "asal-usul"/alasan spesifik (Hutang Belum Difaktur, Uang Muka, HPP, dll) dibahas detail di [06-accounting-business.md](06-accounting-business.md).
