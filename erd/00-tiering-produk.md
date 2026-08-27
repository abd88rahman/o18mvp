# Tiering Produk: Basic / Standard / Enterprise

Status: catatan tiering wajib dipertimbangkan di **semua** requirement `app/mvp` (dan turunannya di `app/custom`) — menentukan modul/fitur apa yang benar-benar ada di tiap level produk. Diringkas dari [`notes/human-notes/tiering-versi.txt`](../notes/human-notes/tiering-versi.txt) (2026-08-26).

## Daftar Tier

### 1. Basic
- **Cuma modul Accounting** — Sales, Purchase, Inventory, HRIS **tidak ada sama sekali** sebagai fitur lengkap.

**Koreksi 2026-08-26**: Basic ternyata **butuh 1 dokumen non-jurnal** juga — **Purchase Order (PO) versi ringan** (header: vendor, tanggal, keterangan; **plus** `line_ids` sederhana — deskripsi bebas teks + qty + harga satuan, **tanpa** Product/UoM master supaya tidak nambah relasi kompleks). Baris qty+harga ini jadi basis hitung FIFO/Average di akun Persediaan (mekanisme costing persisnya belum dirancang — lihat [06-accounting-business.md § D.1](mvp/06-accounting-business.md)). PO ini jadi dasar/referensi utk Uang Muka Pembelian (wajib), Penerimaan Barang, dan Pembelian — bukan cuma "kesepakatan di luar sistem" seperti draft awal. Workflow-nya `draft` → `confirmed` (bukan `draft`→`posted`, krn PO sendiri **tidak langsung menghasilkan jurnal** — sesuai [00-konvensi-teknis.md](00-konvensi-teknis.md) poin 5). PO ringan ini tetap bagian `c18_account` (bukan `c18_purchase`, yang masih Standard+), nanti di-`_inherit` oleh `c18_purchase` buat nambah Product/UoM, multi-warehouse, & fitur penuh (partial receipt/invoice, dst) — pola sama seperti Partner di-extend lintas tier. **Ini beda karakter dari register Aktiva Tetap** (yang sengaja ditiadakan di Basic) — PO adalah titik cabang aktif ke banyak dokumen turunan, bukan daftar statis tanpa fungsi.

**Breakdown resmi (`notes/human-notes/tiering-versi.txt` baris 21-31, 2026-08-26)** — 2 kategori jurnal, jangan disamaratakan:

1. **"Versi original" — punya form spesifik sendiri dari awal, BUKAN generic**:
   - Jurnal Umum.
   - Kas Bank: Jurnal Kas Masuk (selain piutang customer), Jurnal Kas Keluar (selain utang vendor), Jurnal Transfer antar Kas — lihat [06-accounting-business.md](mvp/06-accounting-business.md).
   - Tutup Buku: Penyesuaian (awal tahun & akhir tahun), Tutup Buku.
2. **"Versi generik" — format jurnal umum polos, tapi menunya dipisah per kelompok modul** (supaya asal-usul transaksi tetap kelacak walau form-nya generic), diganti/di-hide begitu modul aslinya ter-install di tier lebih tinggi:
   - **Siklus Pembelian**: Penerimaan Barang, Pembelian, Uang Muka Pembelian, Pembayaran Vendor, Retur Barang Vendor, Write-off Hutang.
   - **Siklus Penjualan**: Pengiriman Barang, Penjualan, Uang Muka Penjualan, Penerimaan Piutang, Retur Barang Customer, Write-off Piutang.
   - **Aktiva Tetap**: Pengakuan, Penyusutan, Penghapusan, Penjualan, Revaluasi — **semuanya generic** (termasuk Penyusutan, dikoreksi dari catatan sebelumnya yang salah bilang ini "native").
   - **Payroll**: Hutang Gaji, Bayar Gaji.

- Aktiva Tetap tier Basic: cuma daftar aset polos (register) + kelima jenis transaksinya (Pengakuan/Penyusutan/Penghapusan/Penjualan/Revaluasi) diinput manual lewat form generic di bawah menu "Aktiva Tetap" — belum ada kalkulasi otomatis (baru muncul di Standard).
- Partner (dari [c18_common](mvp/02-common-master-data.md)) **tetap ada**, tapi field-nya **tidak selengkap tier Standard** — field yang cuma relevan buat fitur khusus (mis. alamat kirim detail untuk Delivery) tidak perlu ada di tier ini.
- Rincian requirement detail tier ini **akan ditulis terpisah** (belum ada dokumennya).

### 2. Standard
Melengkapi Basic jadi form/dokumen bisnis spesifik — **dikonfirmasi simetris penuh Sales & Purchase**:
- Sales: Sales Order, Delivery, Sales Invoice, Sales Advance, Sales Payment, Sales Return, Sales Write-off.
- Purchase: PO, Goods Receipt, Vendor Bill, Purchase Advance, Vendor Payment, Purchase Return, Write-off Hutang.
- Akuisisi Aktiva Tetap, penyusutan otomatis, drill-down (dari laporan ke jurnal ke dokumen sumber).
- **Payroll masih manual** — cuma 2 form: Jurnal Gaji dan Jurnal Pembayaran Gaji (format jurnal umum, sama pola dengan Basic), **tanpa** sistem payroll (belum hitung otomatis PPh 21/BPJS/dst).

### 3. Enterprise (Customize)
- **HRIS lengkap**: data karyawan, departemen, job posisi, cuti, lembur, absen, payroll + konfigurasinya — menggantikan 2 form jurnal manual (Gaji/Pembayaran Gaji) dari tier Standard dengan sistem payroll penuh.
- Fitur lain yang spesifik dibutuhkan client (kustomisasi bebas per klien, masuk `app/custom`).

## Mekanisme Teknis: Inheritance Antar Tier (Dikonfirmasi 2026-08-26)

Tiering **bukan** toggle/feature-flag runtime, dan **bukan** 3 dokumen ERD terpisah per tier (1 dokumen ERD tetap cukup, mis. [06-accounting-business.md](mvp/06-accounting-business.md), meskipun scope-nya lintas tier) — melainkan **rantai modul yang saling `_inherit`**, tiap tier lebih tinggi meng-**hide** form generic tier di bawahnya lalu menggantikan dengan fitur lengkap:

```
c18_account (Basic)
  - Jurnal Umum, Kas Bank (Kas Masuk/Keluar/Transfer), Tutup Buku
    -> form SPESIFIK ("versi original"), fitur asli Accounting, bukan placeholder
  - Jurnal Penjualan/Pembelian, Aktiva Tetap (Pengakuan/Penyusutan/Penghapusan/Penjualan/Revaluasi),
    Jurnal Gaji/Bayar Gaji
    -> form GENERIC ("versi generik"), menu dipisah per kelompok modul, krn modul aslinya belum ada
      |
      | _inherit (tambah depends)
      v
c18_sale, c18_purchase (+ fitur Aktiva Tetap otomatis di c18_account sendiri) (Standard)
  - depends ke c18_account
  - HIDE menu/form generic "Sales"/"Purchase"/"Aktiva Tetap" dari c18_account
  - GANTI dengan fitur lengkap: SO/PO, Delivery/Receipt, Invoice/Bill, akuisisi+penyusutan otomatis, dst
  - Jurnal Umum/Kas Bank/Tutup Buku dari Basic TETAP DIPAKAI APA ADANYA (bukan placeholder, tidak diganti)
  - Sisa yang masih generic dari Basic: form Jurnal Gaji & Jurnal Pembayaran Gaji (belum ada Payroll)
      |
      | _inherit (tambah depends)
      v
c18_hris (Enterprise, 1 modul gabungan data karyawan + payroll)
  - depends ke modul Standard (khususnya yg punya form Jurnal Gaji generic)
  - HIDE form Jurnal Gaji/Jurnal Pembayaran Gaji generic
  - GANTI dengan sistem Payroll lengkap (PPh 21, BPJS, payslip, dst) + data karyawan/attendance/time off
```

**Cara "hide/ganti" (dikonfirmasi 2026-08-26)**: override langsung by **xmlid**, bukan `groups`/context:
- Kalau yang diganti cuma **menu** (`ir.ui.menu`) — modul tier lebih tinggi bikin `<record id="c18_account.menu_xxx_generic" model="ir.ui.menu">` (referensi xmlid milik modul tier bawah), timpa field `action` supaya nunjuk ke action baru (fitur lengkap). **Tidak perlu** `_inherit`/xpath — `ir.ui.menu` bukan view QWeb, module yang di-load belakangan (dependency order) menang overwrite by id.
- Kalau yang perlu diubah itu **struktur form/view** (bukan cuma ganti tujuan menu) — baru pakai `_inherit` + xpath `position="replace"` (pola sama seperti override flyout menu di `c18_theme`).
- Untuk kasus "menu Sales tadinya nunjuk form jurnal umum, sekarang nunjuk Sales Order lengkap" — itu murni ganti `action` di menu yang sama (opsi pertama), data lama yang sudah terlanjur diinput lewat form generic tetap aman/bisa ditelusuri (tidak dihapus/di-uninstall, cuma menu-nya yang dialihkan).

**Implikasi ke `02-common-master-data.md`** (dikoreksi 2026-08-26, koreksi kedua di hari yang sama — Product ternyata dibutuhkan dari Basic juga) — `c18_common` **tidak monolitik**, split by model & field sesuai tier:
- Partner (`_inherit res.partner`) — bagian dari `c18_account` sendiri (Basic), dipakai buat AR/AP di jurnal manapun (generic maupun spesifik).
- **Product (`c18.product`) — ternyata perlu dari Basic juga** (bukan Standard+ seperti draft sebelumnya), krn PO ringan (lihat [06-accounting-business.md § D.1 poin 0](mvp/06-accounting-business.md)) butuh referensi produk supaya saldo Persediaan bisa dirinci **per produk** (bukan cuma 1 saldo GL nyampur). Versi Basic-nya **disederhanakan**, model ini lahir di `c18_account` (bukan `c18_common`), field-nya cuma: kode (**konvensi prefix menentukan kelompok**, mirip pola CoA — mis. digit/segmen awal = kelompok, sisanya id unik dalam kelompok itu; skema prefix persis belum dirancang), nama, tipe (Barang Stok / Jasa / Barang Non Stok), `is_purchaseable`/`is_saleable` (2 boolean terpisah, non-exclusive). **Tidak ada kategori sebagai field/model terpisah** (diganti konvensi kode), dan **tidak ada UoM** di Basic (qty polos, tanpa satuan/konversi).
- **UoM (`c18.uom.uom`) — tetap Standard+ saja**, ditambah `c18_purchase`/`c18_sale`/`c18_stock` yang `_inherit` `c18.product` (nambah `uom_id` + tabel konversi antar satuan) — bukan bikin model Product baru dari nol, pola sama seperti PO ringan di-extend.

**Implikasi ke deployment**: tier suatu klien ditentukan dari **modul mana saja yang di-install** (`c18_account` doang, termasuk extend Partner + Product sederhana + PO ringan = Basic; + `c18_sale`/`c18_purchase`/`c18_stock` + UoM + fitur penuh = Standard; + payroll = Enterprise) — konsisten dengan prinsip "1 klien = 1 repo", `app/custom` klien itu tinggal declare `depends` ke modul tier yang sesuai.

## Pemetaan Dokumen Requirement `erd/mvp/` ke Tier

| Dokumen | Tier | Catatan |
|---|---|---|
| [01-accounting-foundation.md](mvp/01-accounting-foundation.md) | **Semua tier** (fondasi, ada di `c18_account`) | GL/Chart of Accounts/Journal/Move dipakai semua tier, cuma UI-nya beda. |
| [02-common-master-data.md](mvp/02-common-master-data.md) | **Terpisah per model & field** (dikoreksi 2026-08-26) | Partner: **semua tier** (dipakai `c18_account` buat AR/AP). Product: **semua tier juga** — versi Basic disederhanakan (kode dg konvensi prefix, nama, tipe, is_purchaseable/is_saleable; tanpa kategori model & tanpa UoM), lahir di `c18_account`. UoM (+kategori kalau nanti dibutuhkan) baru jadi dependency Standard+ (`c18_purchase`/`c18_sale`/`c18_stock` extend `c18.product`). |
| [03-inventory-foundation.md](mvp/03-inventory-foundation.md) | **Standard+** | Tidak ada Inventory sama sekali di Basic. |
| [04-purchase.md](mvp/04-purchase.md) | **Standard+** (dikonfirmasi) | Simetris penuh dengan Sales, sama-sama `_inherit`/depends ke `c18_account`, hide form Jurnal Pembelian generic. |
| [05-sales.md](mvp/05-sales.md) | **Standard+** | Hide form Jurnal Penjualan generic dari `c18_account`. |
| [06-accounting-business.md](mvp/06-accounting-business.md) | **Kas Bank & Jurnal Umum: semua tier (dari Basic, "versi original"). Aktiva Tetap (semua transaksinya) & Laporan Keuangan: Standard+** | Kas Bank (3 form Kas Masuk/Keluar/Transfer) fitur inti Accounting sejak Basic. Aktiva Tetap di Basic **cuma register + form generic** (termasuk Penyusutan — dikoreksi, bukan native), baru dapat form spesifik + otomasi penuh di Standard. |
| [07-hris.md](mvp/07-hris.md) | **Enterprise** (tapi tetap MVP inti, bukan full-custom) | Modul `c18_hris` (1 modul gabungan). Hide form Jurnal Gaji/Pembayaran Gaji generic dari tier Standard. Fitur MVP sederhana (termasuk Attendance/Time Off dasar); kustomisasi lanjutan per klien masuk `app/custom`. |

## Belum Diputuskan / Perlu Digali
- [x] Detail requirement Basic tier (rinci per jenis form jurnal umum, termasuk field Partner/Product versi minimal) — sudah ditulis 2026-08-26 di [06-accounting-business.md § Detail Requirement Tier Basic](mvp/06-accounting-business.md#detail-requirement-tier-basic--field-level-2026-08-26).
