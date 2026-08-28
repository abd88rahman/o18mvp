# app/mvp/

Layer modul minimum yang bisa dipakai berbagai jenis perusahaan (generic, bukan spesifik 1 klien), inherit dari [`app/base/`](../base/). Rencana cakupan (lihat `notes/claude-notes/rencana-pengembangan.md`): Sales, Purchases, Inventory, Accounting, HRIS, plus laporan/cetakan/dasbor/analisis.

**Status (2026-08-27)**: [`c18_basic_erp`](c18_basic_erp/) (nama teknis lama: `c18_account`, di-rename karena scope-nya sudah jauh melebihi "accounting doang") berisi seluruh scope form transaksi tier Basic — fondasi GL, Partner/Product, Kas Bank, PO/SO ringan, siklus Pembelian/Penjualan lengkap (dengan costing FIFO/Average), Aktiva Tetap generik, Payroll, Persediaan (Consume/Opname), dan Tutup Buku. **PENTING: belum smoke test sama sekali ke instance Odoo sungguhan.** Lihat [erd/mvp/00-status-requirement.md](../../erd/mvp/00-status-requirement.md).

Tiap module bisnis yang bikin root menu sendiri wajib di-reparent ke `c18_theme.menu_erp_root` (lihat [erd/base/02-tema-menu.md](../../erd/base/02-tema-menu.md)) dan set `'application': False` di manifest-nya — jangan bikin app top-level baru.
