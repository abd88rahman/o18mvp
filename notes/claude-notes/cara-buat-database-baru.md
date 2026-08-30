# Cara Bikin Database Baru (Lewat CLI, Bukan Database Manager UI)

Prosedur yang dipakai Claude saat diminta bikin database baru di container lokal (`app/docker/`) — dipraktikkan pertama kali 2026-08-30 (bikin `test-01`). Beda dari alur "normal" isi form Database Manager di browser (master password, nama db, login, password, country, demo data) — di CLI, tiap item itu jadi langkah terpisah, tidak ada 1 form yang minta semuanya sekaligus.

## Kenapa Lewat CLI, Bukan Database Manager UI

- Tidak perlu screenshot/klik manual, bisa dijalankan otomatis dari sini.
- **Master password** (`admin_passwd` di `app/docker/etc/odoo.conf`) cuma dipakai buat otorisasi Database Manager **web UI** (create/drop/backup/restore lewat browser) — CLI langsung akses container, jadi tidak perlu master password sama sekali.

## Langkah-Langkah

### 1. Buat database + install modul
```bash
docker compose exec -T odoo18-erp odoo -c /etc/odoo/odoo.conf \
  --db_host=db --db_user=odoo --db_password=changeme \
  -d NAMA_DB -i base --without-demo=all --stop-after-init --no-http
```
- `-i base` — minimal, cuma modul inti. Ganti/tambah modul lain kalau sekalian mau langsung install ERP-nya (mis. `-i c18_theme,c18_basic_erp`).
- `--without-demo=all` — skip semua demo data (lihat pertimbangan di bawah).
- `--db_host`/`--db_user`/`--db_password` **wajib diisi manual** — env var `HOST`/`USER`/`PASSWORD` di `docker-compose.yml` cuma dibaca otomatis oleh `/entrypoint.sh`, bukan oleh binary `odoo` yang dipanggil langsung lewat `docker compose exec`.

### 2. Set login admin (default Odoo BUKAN otomatis "admin"/"admin")
CLI `-i` tidak\melalui wizard Database Manager yang biasanya minta isi password admin — user `admin` otomatis dibuat oleh module `base`, tapi passwordnya perlu di-set eksplisit lewat `odoo shell`:
```python
admin = env.ref('base.user_admin')
admin.write({'password': 'admin'})  # atau password lain sesuai permintaan
env.cr.commit()
```
Login default: **`admin` / `admin`** kalau tidak diminta lain oleh user.

### 3. Set Country (menentukan currency default company)
CLI tidak punya opsi `--country`. Kalau tidak diset, company baru default currency **USD** (bukan IDR) — sudah kejadian 2x sesi ini (`test_c18_basic_erp`, `test-01` awal). Wajib diset manual kalau konteksnya Indonesia:
```python
idr = env['res.currency'].with_context(active_test=False).search([('name', '=', 'IDR')], limit=1)
if not idr.active:
    idr.active = True  # IDR inactive by default di Odoo
indonesia = env['res.country'].search([('code', '=', 'ID')], limit=1)
env.company.write({'currency_id': idr.id, 'country_id': indonesia.id})
env.cr.commit()
```

### 4. Demo Data — defaultnya SKIP (`--without-demo=all`)
Alasan: `c18_basic_erp` **tidak punya key `'demo'` di manifest sama sekali** — kalau demo data diaktifkan, yang masuk cuma demo generik `base`/`web` (company/contact bawaan Odoo, tidak relevan sama ERP ini). Jadi defaultnya selalu skip demo, kecuali:
- User eksplisit minta demo data Odoo bawaan (jarang berguna, tapi bisa).
- Suatu saat `c18_basic_erp` **sudah** punya demo data sendiri (lihat rencana di `notes/claude-notes/` kalau nanti dibuat) — baru demo data jadi relevan diaktifkan.

## Checklist Ringkas (kalau diminta "bikin database baru")
1. Tentukan nama db (tanya user kalau tidak disebutkan).
2. `odoo -d NAMA -i <modul> --without-demo=all --stop-after-init --no-http` (isi `--db_host/user/password` dari `.env`).
3. Set password admin via `odoo shell` (default `admin`/`admin` kecuali diminta lain).
4. Set Country=Indonesia + currency=IDR via `odoo shell` (kecuali user minta negara/currency lain).
5. Restart container `odoo18-erp` **WAJIB** kalau abis `-u` update modul yang ubah **Python field/view** (bukan cuma data XML murni) dan mau langsung dicek/dipakai di browser yang sedang jalan — `-u` via CLI itu proses terpisah (`--no-http`), server yang melayani `localhost:8069` punya registry sendiri di memori yang TIDAK otomatis sinkron cuma karena database berubah. Lupa restart → error browser semacam `OwlError: field is undefined` walau server-side (`fields_get`/`odoo shell`) sudah benar (kejadian nyata 2026-08-30, field `inventory_system`). Create db baru murni (belum ada browser session yang pakai) tidak butuh restart.

## Referensi Terkait
- [`app/docker/nginx/README-nginx-erp-url.md`](../../app/docker/nginx/README-nginx-erp-url.md) — soal expose port/proxy, bukan soal create db.
- [`auto-install-database-baru.md`](auto-install-database-baru.md) — daftar modul yang otomatis ter-install begitu database baru dibuat (independen dari prosedur di file ini).
