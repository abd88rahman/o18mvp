# c18_theme

Module dasar yang menampung semua modifikasi level framework/branding Odoo untuk repo ini. Requirement/PRD lengkapnya ada di root repo, folder [`erd/base/`](../../../erd/base/) (dokumen 01-05) — **bukan di sini**, README ini cuma peta kode.

Status: **scaffold awal (2026-08-26), belum smoke test end-to-end.** Lihat [`erd/base/00-status-requirement.md`](../../../erd/base/00-status-requirement.md) untuk detail status tiap requirement.

## Struktur

| File/Folder | Fungsi | Requirement |
|---|---|---|
| `controllers/database.py` | Gate Master Password di depan `/web/database/manager` | [01](../../../erd/base/01-branding-atribut.md) poin 5 |
| `models/ir_http.py` | Expose `brand_name`/`brand_logo`/`brand_favicon` dari `odoo.conf` ke session_info & QWeb | [01](../../../erd/base/01-branding-atribut.md) |
| `static/src/js/user_menu_patch.js` | Hapus item user menu (Documentation/Support/My Odoo.com Account/Install App) | [01](../../../erd/base/01-branding-atribut.md) poin 6 |
| `static/src/js/messaging_menu_patch.js` | Hapus tile "Install Odoo" di messaging menu | [01](../../../erd/base/01-branding-atribut.md) poin 7 |
| `static/src/xml/menu_flyout_submenu.xml` | Flyout submenu (drill arrow) level 3+ | [02](../../../erd/base/02-tema-menu.md) poin 3 |
| `static/src/scss/colors.scss` | Palet warna lime green | [02](../../../erd/base/02-tema-menu.md) poin 1 |
| `static/src/img/` | Logo & favicon custom (placeholder, ganti kalau sudah ada brand final) | [01](../../../erd/base/01-branding-atribut.md) poin 1 |
| `static/src/public/database_manager_gate.qweb.html` | Halaman form Master Password (dirender statis, bukan `ir.ui.view`) | [01](../../../erd/base/01-branding-atribut.md) poin 5 |
| `views/webclient_templates.xml` | Override title/favicon (`web.layout`) & hapus "Powered by Odoo" (`web.login_layout`) | [01](../../../erd/base/01-branding-atribut.md) poin 1-2 |
| `views/erp_root_menu.xml` | 1 root app tunggal "ERP" — module `app/mvp`/`app/custom` reparent ke sini | [02](../../../erd/base/02-tema-menu.md) poin 2 |
| `data/res_partner_data.xml` | Rename OdooBot -> System Bot | [01](../../../erd/base/01-branding-atribut.md) poin 7 |
| `data/mail_templates_email_layouts.xml` | Override "Powered by Odoo" di 2 layout email dasar | [04](../../../erd/base/04-template-email.md) |
| `data/res_company_data.xml` | Placeholder data perusahaan (report_footer, dsb) | [05](../../../erd/base/05-template-report.md) |

## Konfigurasi (`app/docker/etc/odoo.conf`)
Modul ini **wajib** ada di `server_wide_modules` (bukan cuma ter-install biasa) karena override `Database` controller ada di sini — sudah di-set di [`app/docker/etc/odoo.conf.example`](../../docker/etc/odoo.conf.example). Detail alasannya di [01](../../../erd/base/01-branding-atribut.md) "Catatan Teknis Penting".

## Belum Dikerjakan / Perlu Verifikasi
- Smoke test instalasi & semua fitur di atas belum pernah dijalankan ke database Odoo sungguhan.
- Logo backend navbar: belum dicek apakah sumbernya sudah dari `res.company.logo` (seperti report PDF) atau perlu override kode terpisah.
- Pengecekan hardcode string "OdooBot" di tempat lain (lihat [01](../../../erd/base/01-branding-atribut.md) "Belum Diputuskan").
