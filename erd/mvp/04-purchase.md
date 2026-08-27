# Requirement - Siklus Pembelian (`c18_purchase`)

Status: **draft direview (2026-08-26), belum diimplementasikan.**

**Tier: Standard+** (dikonfirmasi simetris dg Sales) — lihat [erd/00-tiering-produk.md](../00-tiering-produk.md). Modul `c18_purchase` (fitur penuh: line item Product/UoM, multi-warehouse, partial receipt/invoice, dst) tidak ada di Basic.

**Koreksi 2026-08-26** — PO (poin 1 di bawah) ternyata **tidak 100% absen** di Basic: ada versi ringan (header + baris qty/harga teks bebas, **tanpa** Product/UoM) yang hidup di `c18_account`, dipakai sebagai dasar Uang Muka Pembelian/Penerimaan Barang/Pembelian (detail di [06-accounting-business.md § D.1 poin 0](06-accounting-business.md)). Modul `c18_purchase` ini nanti `_inherit` model PO ringan itu (bukan bikin model PO baru dari nol) buat nambah Product/UoM, multi-line lengkap, & fitur penuh (partial receipt/invoice, dll) — pola sama seperti Partner di-extend lintas tier, bukan pola "hide generic form" seperti 5 dokumen lain di siklus ini (Penerimaan Barang, Pembelian, dst tetap generic->diganti seperti biasa).

## Posisi dalam Alur
Depends ke [`c18_common`](02-common-master-data.md) (Product, Partner/Vendor), [`c18_stock`](03-inventory-foundation.md) (penerimaan barang → stock move), dan [`c18_account`](01-accounting-foundation.md) (semua transaksi ujungnya jadi jurnal). Jurnal yang relevan sudah didaftar di [01](01-accounting-foundation.md#2-journal--c18accountjournal): Penerimaan Barang, Pembelian, Uang Muka Pembelian, Pembayaran Vendor, Retur Barang Vendor, Write-off Hutang.

Sesuai [erd/00-konvensi-teknis.md](../00-konvensi-teknis.md): zero dependency ke `purchase` bawaan Odoo — model dibangun dari nol. Fitur ERP-nya direncanakan lebih mirip pola `odoo18_accurate` (adopsi software Accurate) daripada workflow native Odoo. Nama modul final: **`c18_purchase`**.

## Scope

### 1. Dokumen dalam Siklus
Alur dokumen (**tanpa Purchase Request** — langsung mulai dari PO; PR bisa jadi custom terpisah per klien kalau nanti dibutuhkan, bukan bagian MVP ini):

1. **Purchase Order (PO)** — ke vendor. Workflow cuma 2 langkah: `draft` → `confirmed` (lihat konvensi state di [erd/00-konvensi-teknis.md](../00-konvensi-teknis.md), tidak pakai approval berjenjang).
2. **Goods Receipt (Penerimaan Barang)** — trigger stock move masuk di `c18_stock`. Mendukung **penerimaan sebagian** (partial) — sisa qty yang belum diterima memunculkan pilihan: buat PO baru untuk sisanya, atau batalkan sisa PO dengan alasan (mis. stok vendor sudah tidak tersedia).
3. **Purchase Invoice / Vendor Bill (Pembelian)** — jadi hutang usaha. Mendukung tagih sebagian (partial invoice), konsisten dengan partial receipt.
4. **Uang Muka Pembelian (Down Payment)** — dibayar duluan sebelum invoice final.
5. **Pembayaran Vendor** — lihat detail pola di bawah.
6. **Retur Barang Vendor (Purchase Return)** — mendukung **retur sebagian** dari 1 Goods Receipt (tidak harus retur penuh 1 dokumen).
7. **Write-off Hutang** — penghapusan piutang yang macet/tidak tertagih.

### 2. Pembayaran Vendor — Pola Ala Accurate
**Dikonfirmasi**: 1 dokumen pembayaran bisa alokasikan ke **banyak invoice sekaligus** (bukan 1:1 sederhana ala native Odoo `account.payment.register`).

Ada field penambah/pengurang nilai pembayaran, dengan istilah **"Deductions"** (bukan "Other Charges") — secara default berarti pengurang nilai bayar, tapi bisa diisi **nilai negatif** kalau maksudnya justru menambah nilai (mis. biaya admin bank yang ditambahkan, bukan dipotong). Ini mengikuti pola yang sudah diputuskan ulang di proyek referensi `odoo18_accurate` (dari native `account.payment.register` jadi model custom ala Accurate).

## Belum Diputuskan / Perlu Digali
_(tidak ada — semua poin utama sudah diputuskan; detail lebih halus menyusul saat implementasi)_
