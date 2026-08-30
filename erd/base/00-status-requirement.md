# Status Ringkasan Requirement - app/base

Catatan pelacakan status tiap dokumen requirement di folder ini, supaya gampang lanjut sesi berikutnya tanpa perlu baca ulang semua file. Update manual tiap kali ada progres/keputusan baru.

Terakhir diupdate: 2026-08-30 (`c18_help` diputuskan jadi **permanen** — status prototype dilepas, PRD ditulis di [06](06-qa-guide-viewer.md), label menu di-rename "Help" → "QA Guide" biar jelas internal-only). Update sebelumnya: 2026-08-27 (`c18_theme` sudah **lolos smoke test** ke instance Odoo sungguhan, hasil sesuai ekspektasi. Rename dari `erp_base_theme` ke `c18_theme` mengikuti konvensi baru, lihat `notes/human-notes/master-plan.txt`.).

## Sudah Selesai / Cukup

| Dokumen | Ringkasan |
|---|---|
| **Branding & Atribut** ([01](01-branding-atribut.md)) | Icon/logo/favicon, hapus "Powered by Odoo", gate Database Manager, user menu (sisakan Shortcuts/Preferences/Log out), Discuss (hapus tile "Install Odoo", rename OdooBot -> System Bot). Sisa: cek hardcode "OdooBot" di tempat lain saat implementasi (bukan blocker requirement). |
| **Tema Warna & Hierarki Menu** ([02](02-tema-menu.md)) | Palet primary **lime green**. Semua module `app/mvp`/`app/custom` jadi kategori di bawah 1 root app tunggal (`application: False` + reparent), bukan multi-app switcher. Flyout submenu level 3+ (ikon `oi-chevron-right`) via override `web.NavBar.SectionsMenu.Dropdown.MenuSlot` pakai nested `<Dropdown>` bawaan Odoo. Pola diadopsi dari proyek referensi `aviat-odoo` yang sudah terverifikasi jalan di database nyata. |
| **Template Email** ([04](04-template-email.md)) | Override `mail.mail_notification_layout` & `mail.mail_notification_light` (2 layout dasar, cover mayoritas email) + `auth_signup` + `portal`. Footer diganti teks berisi `brand_name`. `hr_expense` dikonfirmasi di luar scope. |
| **Template Report PDF** ([05](05-template-report.md)) | Tidak perlu override kode — pemilihan `external_report_layout_id` bebas (semua narik dari `res.company`). Data `res.company` diisi placeholder XML polos di `c18_theme`, admin edit lagi lewat Settings > Companies. |
| **URL Rewrite `/odoo/` → `/erp/`** ([03](03-url-rewrite.md)) | Reverse proxy nginx + `proxy_redirect` (bukan sekadar rewrite path, karena beberapa controller Odoo redirect balik ke `/odoo` sebagai path relatif). Draft config: [`app/docker/nginx/odoo-erp.conf`](../../app/docker/nginx/odoo-erp.conf). Detail TODO (hostname/SSL/nama service) sengaja ditunda ke tahap `app/docker/`. |
| **QA Guide Viewer** ([06](06-qa-guide-viewer.md)) | `c18_help` — viewer dokumen testing (`.rst`, sinkron manual dari `testing/mvp/*.md`) langsung di dalam Odoo, menu "QA Guide". **Internal tester/QA only** — tidak boleh ter-install di database demo/client (tidak ada pembatasan hak akses, murni disiplin operasional). Tidak auto-install, category Hidden. |

## Belum Dibahas / Belum Lengkap
_(tidak ada — semua dokumen requirement app/base sudah lengkap/cukup)_

## Ditunda (Sengaja)
- Detail konfigurasi nginx final (hostname, nama service, SSL) di [03](03-url-rewrite.md) — ditunda ke saat `docker-compose.yml` mulai disusun, bukan bagian requirement.
- Breakdown kategori/menu final per modul bisnis di [02](02-tema-menu.md) — baru konkret saat `app/mvp` mulai dibangun.

## Status Implementasi Kode
- `c18_theme` — **sudah di-scaffold** di [`app/base/c18_theme/`](../../app/base/c18_theme/), requirement (dokumen 01-05) semua sudah lengkap, dan **sudah lolos smoke test** ke instance Odoo sungguhan (hasil sesuai ekspektasi, 2026-08-27).
