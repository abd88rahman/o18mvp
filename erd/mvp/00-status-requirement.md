# Status Ringkasan Requirement - app/mvp

Catatan pelacakan status tiap dokumen requirement di folder ini, supaya gampang lanjut sesi berikutnya tanpa perlu baca ulang semua file. Update manual tiap kali ada progres/keputusan baru.

Terakhir diupdate: 2026-08-26 (07 direview sebagian — modul digabung jadi `c18_hris` (bukan `c18_hr`/`c18_hr_payroll` terpisah), riwayat kontrak bertanggal dikonfirmasi, Attendance/Time Off masuk MVP versi sederhana (HRIS tier Enterprise tapi tetap MVP inti, bukan full-custom), Cost Center & salary rule fleksibel & UMK BPJS dikonfirmasi. Sisa: riset 3 repo referensi payroll blm dilakukan.).

## Sudah Selesai / Cukup

| Dokumen | Ringkasan |
|---|---|
| **Fondasi Accounting/GL** ([01](01-accounting-foundation.md)) | **Cuma fondasi** (level sama dg `c18_common`), bukan modul "Accounting" MVP itu sendiri — lihat [06](06-accounting-business.md) utk itu. Chart of Accounts (data default + 15 tipe akun ala Accurate), ~25 tipe Journal, Account Move/Move Line (`c18.account.*`) + generic reference, Cost Center (field di move line), Multi-currency (kurs transaksi + tabel kurs harian), Periode akuntansi (deteksi murni dari tanggal, tanpa field tambahan). |
| **Fondasi Master Data Bersama** ([02](02-common-master-data.md)) | Partner (`_inherit res.partner`, **semua tier** — multi-alamat/hierarki/VAT sudah gratis dari bawaan), Product (`c18.product`, **Standard+**: tipe Barang Stok/Jasa/Non Stok, bisa dibeli dan/atau dijual), UoM (`c18.uom.uom`, **Standard+**, dengan konversi antar satuan). Warehouse sengaja tidak masuk sini (nanti di modul Inventory). |
| **Fondasi Inventory/Persediaan** ([03](03-inventory-foundation.md)) | **Tier Standard+.** Warehouse 1 level (tanpa sub-lokasi), multi-warehouse tanpa feature flag, Stock Move + generic reference, Stock Reservation (cegah SO menyalip), Serial/Lot dari awal, 3 metode valuasi (FIFO/Average/Specific, tanpa LIFO sesuai PSAK 14) + sistem pencatatan Perpetual/Periodik — keduanya global, cuma bisa diubah setelah tutup buku. Depends ke `c18_common` & `c18_account`. |
| **Siklus Pembelian** ([04](04-purchase.md)) | **Tier Standard+.** PO (tanpa PR) → Penerimaan Barang (partial, ada popup sisa qty) → Vendor Bill (partial) → Uang Muka → Pembayaran Vendor (multi-invoice + field "Deductions" ala Accurate) → Retur (partial) → Write-off. Workflow PO cuma `draft`→`confirmed`. Depends `c18_common`/`c18_stock`/`c18_account`. |
| **Siklus Penjualan** ([05](05-sales.md)) | **Tier Standard+.** SO (tanpa Quotation terpisah) → Delivery (partial) → Sales Invoice (partial) → Uang Muka → Penerimaan Piutang (multi-invoice + Deductions) → Retur (partial) → Write-off. Simetris penuh dg Purchase. Depends `c18_common`/`c18_stock`/`c18_account`. |
| **Accounting (Business Layer)** ([06](06-accounting-business.md)) | Kas Bank (Kas Masuk/Keluar/Transfer — **tier Basic+**, `draft`→`posted`), Aktiva Tetap otomatis (penyusutan garis lurus, PPh Final revaluasi via field manual) & 4 Laporan Keuangan (Neraca/Laba Rugi/Trial Balance/Buku Besar) — **tier Standard+**. Bank Reconciliation & Budget ditunda ke Enterprise. |

## Belum Dibahas / Belum Lengkap

| Dokumen | Ringkasan | Catatan |
|---|---|---|
| **HRIS & Payroll** ([07](07-hris.md)) | Modul `c18_hris` (gabungan). Data karyawan + kontrak (riwayat bertanggal) + Attendance/Time Off sederhana + payroll (salary rule fleksibel, PPh 21 TER, BPJS+UMK, Cost Center). **Tier Enterprise, tapi tetap MVP inti.** | Sisa: riset ke 3 repo referensi payroll (`odoo18-toso`, `odoo18-cep`, `odoo10-kp3`) buat detail teknis PPh 21/BPJS/salary rule. |

## Ditunda (Sengaja)
- **Bank Reconciliation** & **Budget** — ditunda ke tier Enterprise, bukan bagian MVP (Basic/Standard). Lihat [06](06-accounting-business.md).

## Modul Belum Punya Kode Custom Sama Sekali
- `c18_account` — **belum dibuat sama sekali**, tapi requirement (dokumen 01 fondasi + 06 Kas Bank/Aktiva Tetap/Laporan, 1 modul yang sama) sudah cukup lengkap, **siap mulai implementasi**.
- `c18_common` — **belum dibuat sama sekali**, tapi requirement (dokumen 02) sudah cukup lengkap, **siap mulai implementasi**.
- `c18_stock` — **belum dibuat sama sekali**, tapi requirement (dokumen 03) sudah cukup lengkap, **siap mulai implementasi**.
- `c18_purchase` — **belum dibuat sama sekali**, tapi requirement (dokumen 04) sudah cukup lengkap, **siap mulai implementasi**.
- `c18_sale` — **belum dibuat sama sekali**, tapi requirement (dokumen 05) sudah cukup lengkap, **siap mulai implementasi**.
- `c18_hris` — **belum dibuat sama sekali**, requirement (dokumen 07) masih perlu riset payroll lebih lanjut sebelum siap implementasi penuh.
