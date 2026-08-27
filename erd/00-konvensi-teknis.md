# Konvensi Teknis Lintas Modul

Status: catatan konvensi wajib yang berlaku untuk semua layer (`app/base`, `app/mvp`, `app/custom`), bukan requirement per-modul. Ditambah seiring berjalannya development kalau ada konvensi baru yang disepakati. Diringkas dari [`notes/human-notes/master-plan.txt`](../notes/human-notes/master-plan.txt) (2026-08-26).

## Daftar Konvensi

### 1. Zero dependency ke app bisnis bawaan Odoo
Misi proyek: membangun ERP penuh (Accounting, Purchase, Stock, HR, Payroll, dst) di atas Odoo, dengan struktur modul **full custom** — hanya bergantung pada app bawaan Odoo `base` (+ `web`, keduanya wajib ada di setiap instalasi Odoo, plus framework layer sejenis seperti `mail`/`auth_signup`/`portal` yang memang dipakai [`c18_theme`](../app/base/c18_theme/)).

**Tidak memakai app bisnis bawaan Odoo lain sama sekali, di modul manapun**: `account`, `sale`, `purchase`, `stock`, `hr`, `contacts`, dst. Fitur ERP-nya sendiri (accounting, sales, purchase, inventory) direncanakan lebih mirip pola `odoo18_accurate` (adopsi software Accurate) daripada workflow native Odoo.

**Klarifikasi "bagian `base`" vs "addon terpisah" (2026-08-26, dari [erd/mvp/02](mvp/02-common-master-data.md))** — tidak semua model bawaan Odoo levelnya sama:
- Model yang **genuinely berada di dalam `base`** (dicek langsung ke source, bukan diasumsikan) — boleh di-`_inherit` (extend), bukan dibangun ulang dari nol. Contoh: `res.partner` (`odoo/addons/base/models/res_partner.py`). Extend ini zero-cost (tidak nambah dependency di luar base+web) dan gratis dapat fitur matang (hierarki company↔contact, multi-alamat, VAT, dsb) — reinvent dari nol di sini pemborosan tanpa manfaat.
- Model yang ada di **addon terpisah** dari `base` — walau bukan "app bisnis" (`sale`/`purchase`/`stock`/`hr`), tetap dibangun dari nol demi konsisten cuma depends base+web. Contoh: `product.template`/`product.product` (addon `product`) dan `uom.uom`/`uom.category` (addon `uom`) — keduanya di luar `base`, jadi tidak di-extend, dibangun jadi `c18.product`/`c18.uom.uom` sendiri.

**Cara cek**: jangan asumsi dari nama model — cek langsung file mana yang mendefinisikan `_name` tsb ada di folder `odoo/addons/base/` (bagian base) atau di `addons/<nama-addon-lain>/` (addon terpisah).

### 2. Prefix module & model/tabel: `c18_*` (satu prefix, dipakai di dua-duanya)
Tiap modul custom (`app/mvp`, `app/custom`, dan modul framework di `app/base`) jadi addon terpisah dengan prefix folder `c18_*` — konsisten dengan [`app/base/c18_theme`](../app/base/c18_theme/) yang sudah discaffold. Prefix ini diadopsi dari proyek referensi `aviat-odoo`, dipakai apa adanya (bukan disesuaikan per-nama-klien) karena sifatnya generik, bukan nama brand tertentu.

Nama class Python dan nama model (jadi nama tabel di DB) juga pakai prefix **`c18_*` yang sama** (bukan prefix beda seperti awalnya direncanakan `o18_*`, disederhanakan 2026-08-26) — supaya walau ada nama model/tabel yang identik dengan aslinya Odoo, tetap aman karena sudah ber-namespace sendiri. Contoh: `c18.account.account` (bukan `account.account`), modul `c18_account` isinya model `c18.account.*`.

**Referensi daftar model/tabel asli Odoo** (untuk dicek biar tidak collision & sebagai peta fitur): [`notes/human-notes/modul-asli-odoo.txt`](../notes/human-notes/modul-asli-odoo.txt). Pendamping di level addon/app (bukan model): [`notes/claude-notes/daftar-modul-odoo18-community.md`](../notes/claude-notes/daftar-modul-odoo18-community.md) — daftar lengkap addon yang genuinely ada di Community, digenerate langsung dari source (bukan ingatan).

**2 koreksi hasil cross-check ke source Odoo 18 Community asli (2026-08-26)** terhadap `modul-asli-odoo.txt`, catatan itu sendiri tidak diedit sesuai kesepakatan (lihat `notes/human-notes/`), jadi dicatat di sini:
- `purchase_request`/`purchase_request_line` **bukan modul asli Odoo** — itu module OCA (`purchase-workflow`, pihak ketiga/komunitas), tidak ada di source Odoo resmi manapun (Community maupun Enterprise).
- `documents_document`, `sign_request`, `sign_request_item` (Documents & Sign) **Enterprise-only** — tidak ada di source Odoo 18 Community (folder `sign/`, `documents/` tidak ada sama sekali di `addons/` Community). Tidak akan tersedia di deployment kita (image resmi `odoo:18` = Community) kecuali sengaja pasang Enterprise.

### 3. Nama field
Bahasa Inggris yang berlaku umum di Odoo/sistem ERP lain, bukan Inggris percakapan sehari-hari (mis. ikuti konvensi penamaan field yang lazim dipakai Odoo/Accurate, bukan terjemahan harfiah).

### 4. Cost Center menggantikan Account Analytic
Fitur `account.analytic.*` bawaan Odoo diganti istilah "Cost Center" di modul kita, tapi **cara kerjanya tidak sepenuhnya sama** dengan Analytic Accounting Odoo. Detail lengkap sudah ditulis di [erd/mvp/01-accounting-foundation.md](mvp/01-accounting-foundation.md) poin 4 — field `cost_center_id` di level move line, master data fleksibel (departemen atau project).

### 5. Workflow state dokumen: 2 langkah saja (bukan approval berjenjang)
Dokumen transaksi (PO, SO, dsb) **cukup 2 state**: `draft` → `confirmed` (bukan berjenjang kayak `draft` → `to approve` → `approved` ala native Odoo). Tujuan state `confirmed` cuma buat membedakan dokumen yang sudah final (jadi readonly, tidak bisa diedit bebas lagi) dari yang masih draft — **bukan** untuk implementasi approval hierarchy/multi-level.

Khusus **dokumen yang langsung menghasilkan jurnal** — bukan cuma `c18.account.move` sendiri, tapi juga dokumen Accounting business layer yang memang setara jurnal (Kas Bank, Aktiva Tetap — lihat [erd/mvp/06-accounting-business.md](mvp/06-accounting-business.md)) — istilah state-nya beda konvensi (ikut istilah akuntansi umum): `draft` → `posted`, bukan `draft` → `confirmed`. Dokumen bisnis yang jurnalnya baru muncul belakangan lewat proses lain (PO/SO — jurnal muncul pas Goods Receipt/Delivery/Invoice, bukan pas PO/SO sendiri di-confirm) tetap pakai `draft` → `confirmed`.

Kalau suatu saat modul tertentu genuinely butuh approval berjenjang, itu keputusan khusus modul itu (dicatat di requirement modul tsb, bukan menyalahi konvensi umum ini).

**Ditentukan (2026-08-26)** saat membahas [erd/mvp/04-purchase.md](mvp/04-purchase.md) (Purchase Order).

## Prosedur Menambah Konvensi Baru
- Konvensi ditambahkan di sini kalau sifatnya wajib berlaku di banyak/semua modul (bukan spesifik satu modul saja) — kalau spesifik 1 modul, taruh di dokumen requirement modul itu (`erd/<layer>/NN-*.md`).
- Tulis: apa aturannya, alasan/tujuannya, dan catatan implementasi kalau ada modul existing yang belum konsisten dengan aturan ini.
