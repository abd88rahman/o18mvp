# Requirement - Siklus Penjualan (`c18_sale`)

Status: **draft direview (2026-08-26), belum diimplementasikan.**

**Tier: Standard+** — lihat [erd/00-tiering-produk.md](../00-tiering-produk.md). Tidak ada di tier Basic (Basic cuma modul Accounting polos).

## Posisi dalam Alur
Depends ke [`c18_common`](02-common-master-data.md) (Product, Partner/Customer), [`c18_stock`](03-inventory-foundation.md) (pengiriman barang → stock move keluar, konsumsi Stock Reservation), dan [`c18_account`](01-accounting-foundation.md) (semua transaksi ujungnya jadi jurnal). Jurnal yang relevan sudah didaftar di [01](01-accounting-foundation.md#2-journal--c18accountjournal): Pengiriman Barang, Penjualan, Uang Muka Penjualan, Penerimaan Piutang, Retur Barang Customer, Write-off Piutang.

Sesuai [erd/00-konvensi-teknis.md](../00-konvensi-teknis.md): zero dependency ke `sale` bawaan Odoo — model dibangun dari nol. **Simetris penuh dengan [Purchase](04-purchase.md)**, arah kebalikan (piutang, bukan hutang). Nama modul final: **`c18_sale`**.

## Scope

### 1. Dokumen dalam Siklus
**Tanpa tahap Quotation terpisah** — langsung mulai dari Sales Order (SO), yang berfungsi sekaligus sebagai penawaran harga ke calon pembeli selama masih status `draft` (workflow 2 langkah `draft` → `confirmed`, konvensi [erd/00-konvensi-teknis.md](../00-konvensi-teknis.md) poin 5 — termasuk untuk diskon SO, tidak ada approval berjenjang).

1. **Sales Order (SO)** — ke customer.
2. **Delivery (Pengiriman Barang)** — trigger stock move keluar di `c18_stock`, konsumsi Stock Reservation. **Mendukung pengiriman sebagian** (partial).
3. **Sales Invoice (Penjualan)** — jadi piutang usaha. **Mendukung tagih sebagian** (partial invoice).
4. **Uang Muka Penjualan (Down Payment)** — diterima duluan sebelum invoice final.
5. **Penerimaan Piutang (Customer Receipt)** — pola sama dengan Pembayaran Vendor di Purchase: 1 dokumen bisa alokasikan ke banyak invoice sekaligus + field **"Deductions"** (penambah/pengurang, bisa diisi nilai negatif).
6. **Retur Barang Customer (Sales Return)** — **mendukung retur sebagian**, simetris dengan Purchase Return.
7. **Write-off Piutang** — penghapusan piutang yang macet/tidak tertagih.

Semua poin di atas **simetris penuh dengan [Purchase](04-purchase.md)** — desain & mekanismenya sama persis, cuma arah dokumen & akun (piutang vs hutang) yang beda.

## Belum Diputuskan / Perlu Digali
_(tidak ada — semua poin sudah diputuskan simetris dengan Purchase; detail lebih halus menyusul saat implementasi)_
