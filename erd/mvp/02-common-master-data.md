# Requirement - Fondasi Master Data Bersama (`c18_common`)

Status: **draft direview (2026-08-26), belum diimplementasikan.**

**Tier (dikoreksi 2026-08-26)** — lihat [erd/00-tiering-produk.md](../00-tiering-produk.md):
- **Partner: semua tier** (Basic+) — dipakai `c18_account` buat AR/AP di jurnal manapun, generic maupun spesifik.
- **Product: semua tier juga** (koreksi dari draft awal yang bilang Standard+ saja) — PO ringan di Basic ([06-accounting-business.md § D.1 poin 0](06-accounting-business.md)) butuh referensi produk supaya saldo Persediaan bisa dirinci per produk. Versi Basic disederhanakan: **tanpa kategori** (model/field terpisah — diganti konvensi prefix di `kode`, mirip pola CoA) dan **tanpa UoM**. Model lahir di `c18_account` (bukan `c18_common`).
- **UoM: tetap Standard+ saja** — baru ditambah `c18_purchase`/`c18_sale`/`c18_stock` yang `_inherit` `c18.product` (nambah `uom_id` + tabel konversi), bukan bikin model Product baru dari nol.

## Kenapa Ini Duluan (sebelum Sales/Purchase/Inventory)
Sales, Purchase, dan Inventory sama-sama butuh master data yang **sama persis**, bukan masing-masing punya versi sendiri — supaya 1 produk/1 partner konsisten dipakai lintas modul (mis. produk yang dibeli di Purchase adalah produk yang sama yang dilacak stoknya di Inventory dan dijual di Sales). Kalau tiap modul bikin master data sendiri-sendiri, bakal duplikasi & tidak sinkron.

Pola ini mengikuti proyek referensi `aviat-odoo` (`c18_common` — "model baru lintas cluster", terpisah dari `c18_account`, dipakai bareng modul bisnis lain). Nama modul final: **`c18_common`**.

**Penyesuaian aturan zero-dependency (2026-08-26)** — dicek langsung ke source, ternyata `res.partner` **genuinely bagian dari `base`** (`odoo/addons/base/models/res_partner.py`), beda posisi dari `product.template`/`uom.uom` yang ada di addon **terpisah** (`product`, `uom` — bukan bagian `base`). Jadi:
- **Partner**: **extend `res.partner` via `_inherit`** (bukan bikin model baru) — zero-cost karena tetap di dalam `base`, sekalian dapat gratis fitur matang yang sudah ada (hierarki company↔contact, multi-alamat via child partner + field `type`, VAT/NPWP, rekening bank, dsb). Reinvent dari nol di sini dianggap pemborosan tanpa manfaat, karena tidak ada resiko "app bisnis" yang ikut kebawa.
- **Product & UoM**: **tetap dibangun dari nol** (`c18.product`, `c18.uom.uom`) — karena `product`/`uom` addon terpisah dari `base`, jadi extend ke situ berarti nambah dependency di luar base+web. Meskipun `product`/`uom` sendiri bukan "app bisnis" (bukan `sale`/`purchase`/`stock`/`hr`), diputuskan tetap dari nol demi konsisten cuma depends base+web.

Detail ini akan dipromosikan ke [erd/00-konvensi-teknis.md](../00-konvensi-teknis.md) sebagai klarifikasi aturan zero-dependency (bedakan "bagian `base`" vs "addon terpisah walau bukan app bisnis").

**Warehouse/Location tidak masuk modul ini** — itu spesifik jadi bagian modul Inventory sendiri (Sales/Purchase numpang pakai lewat depends ke situ, bukan sebaliknya).

## Scope

### 1. Partner/Contact — `_inherit res.partner`
**Bukan model baru** — extend `res.partner` bawaan (lihat penjelasan di atas). Customer dan Vendor pakai partner yang sama (bukan 2 tabel terpisah), dibedakan lewat field tambahan kita (`is_customer`, `is_vendor` — bisa keduanya sekaligus). Dipakai juga oleh `c18_account` (partner di tiap transaksi piutang/hutang).

Field tambahan yang kita perlukan di atas `res.partner` bawaan: NPWP (kalau belum ada field standarnya), termin pembayaran default. Multi-alamat (tagih vs kirim) & NPWP/VAT dasar, hierarki company↔contact — **sudah otomatis tersedia** dari `res.partner` bawaan (child partner dengan field `type`), tidak perlu dibangun ulang.

### 2. Product — `c18.product`
Master barang/jasa, dipakai PO ringan (Basic, [06-accounting-business.md § D.1](06-accounting-business.md)) sampai Sales/Purchase/Inventory penuh (Standard+).

**Field level Basic** (lahir di `c18_account`):
- Kode — **konvensi prefix menentukan kelompok** (mirip pola CoA: segmen awal = kelompok, sisanya id unik dalam kelompok itu). **Format bebas karakter** (dikonfirmasi 2026-08-26) — tidak ada validasi struktur digit/panjang yang dipaksakan sistem, kode cuma field teks biasa; pengelompokan murni konvensi manual milik klien (mis. urutan huruf/angka apapun yang mereka pakai), bukan di-parse/divalidasi otomatis oleh sistem. **Tidak ada field/model kategori terpisah** — pengelompokan cukup dari parsing kode ini (manual, oleh manusia yang baca, bukan otomatis oleh sistem).
- Nama.
- **Tipe** (selection): Barang Stok, Jasa, Barang Non Stok — cuma "Barang Stok" yang nilainya masuk & di-track di akun Persediaan (FIFO/Average); Jasa & Barang Non Stok langsung ke akun Beban/lawan lain, tanpa costing.
- `is_purchaseable` / `is_saleable` — 2 field boolean terpisah (bukan selection/multi), karena 1 produk bisa salah satu atau keduanya sekaligus (mis. bahan baku cuma dibeli, produk jadi cuma dijual, tapi ada juga produk yang dua-duanya).

**Field tambahan mulai Standard** (`_inherit` `c18.product`, ditambah `c18_purchase`/`c18_sale`/`c18_stock`): `uom_id` + tabel konversi antar-UoM (lihat poin 3), harga jual/beli default.

~~Belum Diputuskan: skema prefix kode Product~~ — **selesai 2026-08-26**, lihat di atas (bebas karakter, tidak divalidasi sistem).

### 3. UoM (Satuan) — `c18.uom.uom`
Satuan dasar (pcs, kg, box, dst), dipakai di Product, Sales, Purchase, Inventory.

**Perlu konversi antar satuan** dari awal (bukan ditunda) — kasus nyata: UoM saat beli beda dengan UoM saat jual, atau beda lagi kalau dipakai sendiri buat produksi barang. Jadi tiap produk bisa punya beberapa UoM dengan faktor konversi ke 1 UoM dasar/acuan.
