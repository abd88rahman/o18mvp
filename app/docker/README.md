# app/docker/

Deployment lokal/production Odoo 18 untuk repo ini (`db`, `odoo18-erp`, `nginx` — lihat `docker-compose.yml` di folder ini).

Project name di-set eksplisit `name: o18mvp` (baris pertama `docker-compose.yml`) — supaya nama container jadi `o18mvp-<service>-1` (mis. `o18mvp-db-1`), bukan otomatis dari nama folder `odoo18_mvp1` yang panjang. Ini tidak mempengaruhi networking antar service (`nginx`→`odoo18-erp`, `odoo18-erp`→`db` tetap resolve pakai nama **service**, bukan nama container).

## Setup Awal (Sekali Saja per Clone/Environment)

File berisi password/config asli **tidak ikut di-commit** (lihat `.gitignore` di folder ini). Sebelum `docker compose up` pertama kali, copy dulu template-nya (dari dalam folder `app/docker/`):

```bash
cd app/docker
cp .env.example .env
cp etc/odoo.conf.example etc/odoo.conf
```

Lalu edit isi `.env` dan `etc/odoo.conf` sesuai kebutuhan:
- `.env` — `POSTGRES_PASSWORD` (jangan biarkan `changeme` di production).
- `etc/odoo.conf` — `admin_passwd` (Master Password Database Manager) dan `brand_name` (nama produk ERP-nya).

## Menjalankan

```bash
cd app/docker
docker compose up -d
```

(Path addon di-mount relatif `../base`, `../mvp`, `../custom` — jalankan `docker compose` dari dalam folder `app/docker/`, bukan dari root repo.)

## Struktur
| Folder/File | Isi |
|---|---|
| `etc/odoo.conf` | Config Odoo asli (di-mount ke container) — **gitignored**, hasil copy dari `odoo.conf.example`. |
| `etc/odoo.conf.example` | Template yang di-commit, aman (tanpa password asli). |
| `nginx/` | Config reverse proxy nginx — lihat `nginx/README-nginx-erp-url.md`. |
| `pgdata/` | Bind mount native data Postgres (lihat `notes/human-notes/master-plan.txt` — sengaja bukan Docker named volume). |

Requirement/keputusan desain di balik konfigurasi ini ada di `erd/base/` (01, 03, 05).
