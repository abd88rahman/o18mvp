# odoo18_mvp1

ERP full-custom berbasis framework Odoo 18 Community (deploy via Docker) — bukan konfigurasi modul bawaan Odoo, semua fitur bisnis dibangun dari nol. Lihat [`notes/claude-notes/rencana-pengembangan.md`](notes/claude-notes/rencana-pengembangan.md) untuk latar belakang & rencana lengkap.

## Mulai Sesi Kerja Baru? Baca Ini Dulu
1. [`notes/claude-notes/last-session.md`](notes/claude-notes/last-session.md) — titik akhir sesi sebelumnya & langkah berikutnya.
2. [`notes/claude-notes/rencana-pengembangan.md`](notes/claude-notes/rencana-pengembangan.md) — rangkuman rencana & status terkini, selalu update.
3. [`erd/00-konvensi-teknis.md`](erd/00-konvensi-teknis.md) & [`erd/00-tiering-produk.md`](erd/00-tiering-produk.md) — aturan wajib lintas modul (prefix, zero-dependency, tiering Basic/Standard/Enterprise).

## Struktur Repo

```
root
├── app/            # kode
│   ├── base/       # modul framework/branding (c18_theme)
│   ├── mvp/        # modul bisnis inti (c18_account, c18_common, c18_stock, c18_purchase, c18_sale, c18_hris)
│   ├── custom/     # modul khusus 1 klien (1 klien = 1 repo)
│   └── docker/     # docker-compose.yml, config Odoo, nginx
├── erd/            # requirement/PRD (dokumen NN-topik.md per layer + 00-status-requirement.md)
│   ├── base/
│   └── mvp/
└── notes/
    ├── human-notes/    # catatan mentah milik user — JANGAN diedit
    └── claude-notes/   # dokumen rapi hasil rangkuman Claude
```

## Jalankan Docker (Lokal)
```bash
cd app/docker
cp .env.example .env
cp etc/odoo.conf.example etc/odoo.conf
docker compose up -d
```
Detail: [`app/docker/README.md`](app/docker/README.md).

## Status Singkat
- `app/base/c18_theme` — discaffold penuh, belum smoke test.
- `erd/mvp/` — 7 dokumen requirement (fondasi Accounting, master data, Inventory, Purchase, Sales, Accounting business layer, HRIS) sudah direview & ditandai tier; kodenya belum ada.
- Detail lengkap ada di `last-session.md`.
