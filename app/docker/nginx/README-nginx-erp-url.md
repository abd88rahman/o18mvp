# Petunjuk Konfigurasi Nginx — Rewrite `/odoo/` → `/erp/`

Requirement & analisis lengkapnya ada di [`erd/base/03-url-rewrite.md`](../../erd/base/03-url-rewrite.md). File ini cuma petunjuk teknis pemakaian konfigurasi nginx-nya.

## File terkait
- [`odoo-erp.conf`](odoo-erp.conf) — draft konfigurasi nginx (belum final, ada beberapa TODO yang perlu diisi sebelum dipakai).

## Cara Kerja Singkat
1. User buka `https://erp.contoh.local/erp/...` → nginx `rewrite` path itu jadi `/odoo/...` sebelum diteruskan ke Odoo (`proxy_pass`).
2. Kalau Odoo merespons redirect (habis login/logout/dari Database Manager) yang isinya path relatif `/odoo/...`, nginx menimpanya lewat `proxy_redirect` jadi `/erp/...` lagi — supaya address bar browser **tidak** balik sendiri ke `/odoo/...`.
3. Path lain (asset JS/CSS, RPC internal, `/websocket` buat Discuss realtime) **sengaja dibiarkan apa adanya** (`/web/...`, `/websocket`) karena itu dipanggil oleh JS/AJAX di belakang layar, bukan yang tampil di address bar — jadi tidak perlu ikut di-rewrite.

## Yang Wajib Diisi Sebelum Dipakai
Buka `odoo-erp.conf`, cari komentar `TODO`:
1. **Nama upstream** (`odoo18-erp`) — samakan dengan nama service Odoo di `docker-compose.yml`.
2. **`server_name`** (`erp.contoh.local`) — ganti ke domain/hostname sebenarnya.
3. **HTTPS/SSL** — draft ini baru `listen 80` (HTTP polos). Untuk production wajib tambah blok `listen 443 ssl;` + `ssl_certificate`/`ssl_certificate_key` (lihat catatan keamanan di bawah).

## Pemasangan di `docker-compose.yml`
Sudah terpasang — lihat service `nginx` di [`../docker-compose.yml`](../docker-compose.yml) (mount `./nginx/odoo-erp.conf`, depends_on `odoo18-erp`, port `80:80`).

## Catatan Keamanan
- File `odoo-erp.conf` ini **aman** untuk disimpan di repo — tidak ada kredensial/rahasia di dalamnya, cuma aturan routing.
- Kalau nanti menambahkan sertifikat SSL: **jangan commit file `.pem`/`.key` asli** ke repo — cukup mount dari luar (volume/secret), tambahkan pattern-nya ke `.gitignore`.

## Status
Draft (2026-08-26) — `docker-compose.yml` sudah ada, `c18_theme` (dependency di `server_wide_modules`) juga sudah di-scaffold, tapi **belum pernah smoke test** ke instance Odoo sungguhan.
