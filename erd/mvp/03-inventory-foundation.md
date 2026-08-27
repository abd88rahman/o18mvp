# Requirement - Fondasi Inventory/Persediaan (`c18_stock`)

Status: **draft direview (2026-08-26), belum diimplementasikan.**

**Tier: Standard+** — lihat [erd/00-tiering-produk.md](../00-tiering-produk.md). Tidak ada Inventory sama sekali di tier Basic (Basic cuma modul Accounting, transaksi persediaan diinput via jurnal umum generic kalau memang perlu, bukan lewat `c18_stock`).

## Kenapa Ini Duluan (sebelum Sales/Purchase)
Baik Purchase (penerimaan barang) maupun Sales (pengiriman barang) sama-sama butuh konsep pergerakan stok (stock movement) yang identik — supaya 1 transaksi pembelian/penjualan konsisten mempengaruhi saldo persediaan yang sama. Kalau Purchase/Sales masing-masing punya logika stok sendiri, valuasi persediaan bisa tidak sinkron.

Depends ke [`c18_common`](02-common-master-data.md) (Product, UoM) dan [`c18_account`](01-accounting-foundation.md) (buat posting jurnal valuasi persediaan — konvensi generic reference `res_model`/`res_id`). Sesuai [erd/00-konvensi-teknis.md](../00-konvensi-teknis.md): zero dependency ke `stock` bawaan Odoo (addon terpisah dari `base`, sama seperti kasus `product`/`uom`) — model dibangun dari nol. Nama modul final: **`c18_stock`**.

**Warehouse/Location masuk di sini** (sudah diputuskan di [02](02-common-master-data.md), bukan di `c18_common`).

## Scope

### 1. Warehouse — `c18.stock.warehouse`
**Cukup 1 level "Gudang"** (tanpa sub-lokasi/rak/bin granular) — tidak butuh model `location` terpisah.

**Multi-warehouse disediakan dari awal, tanpa feature flag** — user bisa langsung tambah gudang sendiri kapan saja, tidak perlu "mengaktifkan" fitur multi-warehouse dulu (beda dari Odoo native yang multi-warehouse-nya di balik toggle settings).

### 2. Stock Move (Pergerakan Barang) — `c18.stock.move`
Transaksi keluar/masuk/transfer barang, sumbernya dari dokumen lain (Purchase Receipt, Sales Delivery, Transfer antar gudang, Stock Adjustment) via generic reference (`res_model`/`res_id`, konvensi sama dengan `c18_account`).

### 3. Stock Reservation
**Dibutuhkan** — barang yang sudah terikat SO (Sales Order) tapi belum dikirim ditandai "reserved", supaya SO berikutnya **tidak bisa menyalip** ambil stok yang sama. Kalau mau maksa alokasikan ke SO lain, SO yang menahan reservasi itu harus dibatalkan dulu.

### 4. Serial Number / Batch-Lot Tracking
**Dibutuhkan dari awal.** Prasyarat mutlak supaya metode valuasi **Specific Identification** bisa jalan (tanpa ini, tidak mungkin tahu persis unit fisik mana yang terjual buat dilacak cost-nya). Untuk metode FIFO/Average sifatnya pelengkap traceability, bukan wajib buat perhitungan costing.

### 5. Valuasi Persediaan
3 metode didukung: **FIFO, Average, Specific Identification**. **LIFO sengaja tidak disediakan** — PSAK 14 (Persediaan, adopsi dari IAS 2/IFRS) melarang LIFO secara eksplisit, jadi ini juga soal kepatuhan standar akuntansi, bukan cuma preferensi teknis.

**Berlaku global** (1 metode untuk semua produk, bukan per-produk).

### 6. Sistem Pencatatan Persediaan: Perpetual vs Periodik
Pilihan tambahan yang menentukan cara Stock Quant & COGS dihitung:
- **Perpetual** — saldo stok & COGS ter-update real-time tiap ada `stock.move` (tiap penerimaan/pengiriman langsung menghasilkan jurnal COGS saat itu juga).
- **Periodik** — saldo stok tidak di-update terus-menerus; COGS baru dihitung di akhir periode lewat stock opname (saldo awal + pembelian − saldo akhir = COGS), jurnal diposting periodik bukan per-transaksi.

**Berlaku global** juga (bukan per-produk).

**Aturan perubahan setting**: baik metode valuasi maupun sistem pencatatan (perpetual/periodik) **cuma boleh diubah setelah tutup buku** — konsisten dengan konsep periode akuntansi tertutup di [01-accounting-foundation.md](01-accounting-foundation.md) poin 6 (tidak bisa diubah di tengah periode yang masih terbuka).
