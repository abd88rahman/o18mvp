# Rencana Pengembangan ERP Berbasis Odoo 18

> Dokumen ini adalah versi terstruktur dari [`../human-notes/master-plan.txt`](../human-notes/master-plan.txt) (coretan ide awal milik user).
> File itu tetap dipertahankan sebagai catatan mentah/histori ide — lihat `notes/human-notes/` utk semua catatan mentah, `notes/claude-notes/` (folder ini) utk dokumen rapi hasil rangkuman.

## 1. Latar Belakang & Tujuan

Membangun aplikasi ERP dengan basis framework **Odoo versi 18**, di mana:

- Framework Odoo hanya dipakai sebagai fondasi (ORM, workflow engine, UI framework, dsb).
- Seluruh **fitur bisnis dibuat full custom**, tidak sekadar konfigurasi modul bawaan Odoo.
- Source code asli Odoo **tidak boleh terlihat langsung** oleh pengguna/klien akhir — dicapai dengan deploy via **Docker** (image resmi `odoo:18`, source core tidak di-bind-mount ke luar).
- Branding/identitas asli Odoo (logo, nama, "Powered by Odoo", dll) diganti menjadi identitas ERP sendiri.

## 2. Struktur Folder Repo

```
root
├── app/
│   ├── base/        # kode modul: modifikasi inti/branding Odoo (c18_theme)
│   ├── mvp/         # kode modul: fitur minimum, generic utk semua jenis perusahaan
│   ├── custom/      # kode modul: modifikasi khusus 1 klien (1 klien = 1 repo penuh)
│   └── docker/      # orkestrasi deployment (docker-compose.yml, etc/, nginx/, pgdata/)
├── erd/
│   ├── base/        # requirement/PRD utk app/base (dokumen 00-05)
│   ├── mvp/         # requirement/PRD utk app/mvp (belum diisi)
│   └── custom/      # requirement/PRD utk app/custom (belum diisi)
└── notes/
    ├── human-notes/   # catatan mentah user (master-plan.txt, dll) - JANGAN diedit Claude
    └── claude-notes/  # dokumen rapi hasil rangkuman Claude (file ini)
```

3 folder di root: `app/` (kode + deployment), `erd/` (requirement/PRD), `notes/` (catatan kerja, dipisah mentah vs rapi). Pola `app/`+`erd/` diadopsi dari struktur proyek referensi `aviat-odoo` (PT KP3) yang sudah terverifikasi jalan. Sempat beberapa iterasi restrukturisasi (requirement menyatu di `app-base/requirements/` → `erd/` top-level → `docker/` pindah ke dalam `app/` → `master-plan.txt`/dokumen ini dipisah ke `notes/human-notes/`+`notes/claude-notes/`, 2026-08-26).

Relasi antar layer (inherit):

```
app/base  →  app/mvp  →  app/custom
(inti)       (generic)    (spesifik klien ini)
```

## 3. Detail per Folder

### 3.1 `app/base` — Modifikasi Inti Odoo

Berisi perubahan level framework/branding (module rencana: `c18_theme`). Requirement lengkap ada di `erd/base/` (dokumen 01-05, lihat `erd/base/00-status-requirement.md` untuk ringkasan status — **semua sudah lengkap, siap diimplementasikan**):

1. Branding & atribut (icon, logo, "Powered by Odoo", Database Manager gate, user menu, Discuss/OdooBot) — [erd/base/01](../../erd/base/01-branding-atribut.md).
2. Tema warna (lime green) & hierarki menu (1 root app + flyout submenu) — [erd/base/02](../../erd/base/02-tema-menu.md).
3. Rewrite URL `/odoo/` → `/erp/` lewat reverse proxy nginx — [erd/base/03](../../erd/base/03-url-rewrite.md).
4. Template email — [erd/base/04](../../erd/base/04-template-email.md).
5. Template report PDF — [erd/base/05](../../erd/base/05-template-report.md).

### 3.2 `app/mvp` — Modul Minimum (Generic)

Modul dasar yang bisa dipakai oleh berbagai jenis perusahaan, inherit dari `app/base`. Cakupan ternyata **bertingkat per tier produk** (Basic/Standard/Enterprise — lihat [erd/00-tiering-produk.md](../../erd/00-tiering-produk.md)), bukan monolitik. Requirement sudah ditulis 7 dokumen di `erd/mvp/` (lihat `erd/mvp/00-status-requirement.md` untuk status detail):

1. Fondasi Accounting/GL (`c18_account`) — [01](../../erd/mvp/01-accounting-foundation.md). Dipakai **semua tier**.
2. Fondasi Master Data Bersama (`c18_common`: Partner/Product/UoM) — [02](../../erd/mvp/02-common-master-data.md).
3. Fondasi Inventory (`c18_stock`) — [03](../../erd/mvp/03-inventory-foundation.md). Tier **Standard+**.
4. Siklus Pembelian (`c18_purchase`) — [04](../../erd/mvp/04-purchase.md). Tier **Standard+**.
5. Siklus Penjualan (`c18_sale`) — [05](../../erd/mvp/05-sales.md). Tier **Standard+**.
6. Accounting business layer: Kas Bank, Aktiva Tetap, Laporan Keuangan — [06](../../erd/mvp/06-accounting-business.md). Draft saat ini scope **Standard**, versi **Basic** (jurnal umum polos) belum ditulis.
7. HRIS & Payroll (`c18_hr`) — [07](../../erd/mvp/07-hris.md). Tier **Enterprise**, draft sangat kasar, perlu riset ke 3 repo referensi payroll.

Modul 01-05 sudah dianggap requirement-nya cukup lengkap (siap implementasi kode), 06-07 masih draft/perlu digali lebih jauh.

### 3.3 `app/custom` — Modul Custom per Klien

- Inherit dari `app/mvp` dan/atau `app/base` sesuai kebutuhan.
- **1 klien = 1 repo penuh** (bukan wadah multi-klien dalam 1 repo) — jadi folder ini langsung berisi modul-modul custom klien tsb, bukan subfolder per nama klien.
- Detail modifikasi belum didefinisikan (akan disesuaikan per klien saat onboarding), tapi folder sudah disiapkan & di-mount di `docker-compose.yml`.
- Requirement/PRD-nya akan ditulis di `erd/custom/` begitu ada kebutuhan konkret.

### 3.4 `app/docker` — Deployment

Sudah discaffold (2026-08-26):
- `docker-compose.yml` — 3 service: `db` (Postgres 15), `odoo18-erp` (image resmi `odoo:18`), `nginx` (reverse proxy).
- `etc/odoo.conf(.example)` — config Odoo (addons_path 3 layer, server_wide_modules, brand_name, dll).
- `nginx/odoo-erp.conf` + `README-nginx-erp-url.md` — rewrite `/odoo/` → `/erp/`.
- `pgdata/` — bind mount **native** (bukan Docker named volume) khusus data database, sesuai keputusan awal — supaya folder data kelihatan langsung di file manager server.
- `.env(.example)` — kredensial Postgres, file asli di-gitignore, cuma `.example` yang di-commit.

`c18_theme` sudah di-scaffold penuh di `app/base/` (2026-08-26) — manifest, controllers, models, views, data, static, semua sudah ada, tapi **belum pernah smoke test** ke instance Odoo sungguhan. Jalankan dari dalam `app/docker/` (`cd app/docker && docker compose up -d`), bukan dari root repo.

## 4. Requirement / PRD

"Requirement" di repo ini berarti **dokumen PRD** (spesifikasi kebutuhan fungsional per modul), bukan `requirements.txt` python. Konvensinya:
- 1 folder `erd/<layer>/` per layer (`base`/`mvp`/`custom`), isinya file `NN-topik.md` (mis. `01-branding-atribut.md`) + `00-status-requirement.md` sebagai tracker ringkas per layer.
- Kalau ada dependency python yang genuinely dibutuhkan nanti, itu keputusan terpisah (belum relevan sampai ada modul dengan dependency di luar Odoo bawaan).
- Konvensi teknis yang berlaku **lintas semua layer** (bukan spesifik 1 modul) dikumpulkan terpisah di [`erd/00-konvensi-teknis.md`](../../erd/00-konvensi-teknis.md) — prefix `c18_*` (modul & model, disatukan), zero dependency ke app bisnis bawaan Odoo (dg klarifikasi "bagian base" vs "addon terpisah"), field naming, cost center vs analytic, workflow state 2-langkah (draft→confirmed / draft→posted).
- **Tiering produk** (Basic/Standard/Enterprise) — dikumpulkan di [`erd/00-tiering-produk.md`](../../erd/00-tiering-produk.md), menentukan modul/fitur apa yang ada di tiap level produk (mis. Sales/Purchase/Inventory cuma ada mulai tier Standard, HRIS cuma di tier Enterprise).

## 5. Hal yang Masih Terbuka / Perlu Diputuskan

- [ ] Breakdown kategori/menu final per modul `app/mvp` (baru konkret saat modul itu mulai dibangun) — lihat [erd/base/02](../../erd/base/02-tema-menu.md).
- [ ] Detail konfigurasi nginx production (hostname asli, SSL) — lihat [erd/base/03](../../erd/base/03-url-rewrite.md).
- [ ] Skema modul apa saja yang akan ada di `app/custom` (baru bisa didefinisikan saat ada kebutuhan klien konkret).
- [ ] Smoke test `c18_theme` ke instance Odoo sungguhan — belum pernah dijalankan sama sekali.
- [ ] Requirement detail tier **Basic** (jurnal umum polos per jenis, Aktiva Tetap cuma register) — belum ditulis sama sekali, lihat [erd/00-tiering-produk.md](../../erd/00-tiering-produk.md).
- [ ] `erd/mvp/06-accounting-business.md` perlu direvisi/dipecah supaya jelas versi Basic vs Standard.
- [ ] Riset 3 repo referensi payroll (`odoo18-toso`, `odoo18-cep`, `odoo10-kp3`) untuk requirement HRIS ([erd/mvp/07](../../erd/mvp/07-hris.md)).
- [ ] Mekanisme teknis penentuan tier per deployment — murni dari modul apa saja yang di-install (1 klien/repo = 1 tier tetap), atau ada kebutuhan lain?
