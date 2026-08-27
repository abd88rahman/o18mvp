# app/mvp/

Layer modul minimum yang bisa dipakai berbagai jenis perusahaan (generic, bukan spesifik 1 klien), inherit dari [`app/base/`](../base/). Rencana cakupan (lihat `notes/claude-notes/rencana-pengembangan.md`): Sales, Purchases, Inventory, Accounting, HRIS, plus laporan/cetakan/dasbor/analisis.

**Status (2026-08-26): masih kosong** — belum ada module. Requirement/PRD-nya akan ditulis di [`erd/mvp/`](../../erd/mvp/) begitu mulai digarap, belum dimulai.

Tiap module bisnis yang bikin root menu sendiri wajib di-reparent ke `c18_theme.menu_erp_root` (lihat [erd/base/02-tema-menu.md](../../erd/base/02-tema-menu.md)) dan set `'application': False` di manifest-nya — jangan bikin app top-level baru.
