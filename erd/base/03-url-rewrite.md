# Requirement - Rewrite URL `/odoo/` → `/erp/`

Status: **requirement disusun (2026-08-25), belum diimplementasikan — sifatnya "kalo bisa" (nice-to-have), belum prioritas utama.**

## Tujuan
Path URL backend Odoo 18 default (`/odoo/...`) diganti tampilannya jadi `/erp/...` di address bar browser, supaya tidak kelihatan langsung bahwa aplikasi berbasis Odoo.

## Pendekatan: Reverse Proxy (nginx, di layer `app/docker/`)
Dipilih dibanding override routing di level controller/module Odoo — lebih murah, tidak menyentuh source Odoo sama sekali (sejalan dengan prinsip `app/base`: extend/override, bukan patch source), dan tidak berisiko conflict tiap update core Odoo.

**Bukan sekadar rewrite path masuk.** Hasil cek ke source Odoo 18 (`odoo18_original/addons/web/controllers/`), ditemukan beberapa `redirect()` yang hardcode `/odoo` sebagai path **relatif** (bukan URL lengkap):
- `home.py` — controller utama route `/web`, `/odoo`, `/odoo/<path:subpath>`.
- `session.py` — redirect logout default ke `/odoo`.
- `utils.py` — redirect default setelah login.
- `database.py` — redirect dari Database Manager.

Karena path relatif, kalau nginx cuma proxy request path masuk tanpa penanganan tambahan, response `Location` header dari redirect-redirect di atas tetap berisi `/odoo/...` — **address bar browser akan balik sendiri ke `/odoo/...`** persis di momen paling kelihatan (habis login, logout, atau dari Database Manager).

**Solusi tetap murah, tidak perlu sentuh kode Odoo**: tambahkan `proxy_redirect /odoo/ /erp/;` di config nginx, supaya nginx ikut menimpa header `Location` di response, bukan cuma rewrite path request masuk.

Draft konfigurasi nginx-nya sudah ditulis di [`app/docker/nginx/odoo-erp.conf`](../../app/docker/nginx/odoo-erp.conf), penjelasan cara pakainya di [`app/docker/nginx/README-nginx-erp-url.md`](../../app/docker/nginx/README-nginx-erp-url.md) — masih ada beberapa `TODO` (nama upstream, hostname, SSL) yang perlu diisi sebelum benar-benar dipakai.

## Risiko / Hal yang Masih Perlu Dicek
- Asset statis (JS/CSS) yang di-load dari path `/odoo/...` — perlu dipastikan ikut konsisten ter-proxy, kalau tidak muncul broken asset.
- `web/controllers/webmanifest.py` — manifest PWA (`scope`/`start_url`) juga hardcode `/odoo` untuk kebutuhan "Install app" (service worker scope). Prioritas rendah untuk address bar, tapi perlu dicek kalau nanti PWA install dipakai.
- Deep link/bookmark lama yang masih pakai `/odoo/...` — diabaikan karena ini aplikasi baru, belum ada existing user.

## Ditunda ke Tahap Implementasi `app/docker/`
TODO tersisa di `odoo-erp.conf` (nama upstream/service, hostname, SSL) **bukan keputusan desain**, jadi sengaja tidak difinalkan di requirement ini:
- Nama upstream — ikut apa pun nama service Odoo yang dipakai di `docker-compose.yml` nanti.
- Hostname — sifatnya environment-specific (beda dev/staging/prod, dan beda lagi tiap kali repo ini dipakai ulang untuk klien lain — 1 klien = 1 repo/deployment terpisah, lihat `app/custom`) — jadi memang parameter deploy, bukan nilai tetap.
- SSL — wajib ada di production, tapi detail teknisnya (certbot manual/otomatis, atau pindah ke Traefik yang auto-SSL) itu keputusan infrastruktur level `app/docker/`, bukan bagian requirement `app/base`.
