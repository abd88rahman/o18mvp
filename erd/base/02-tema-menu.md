# Requirement - Tema Warna & Hierarki Menu (`c18_theme`)

Status: **requirement disusun (2026-08-25), pola teknis sudah jelas (diadopsi dari proyek referensi terverifikasi), belum diimplementasikan di repo ini.**

Beda scope dengan [01-branding-atribut.md](01-branding-atribut.md): dokumen itu murni ganti atribusi (logo/nama/favicon) **tanpa** ubah warna/layout. Dokumen ini sebaliknya — mengubah tema warna dan struktur navigasi menu, jadi ada perubahan visual/UX yang lebih terasa.

Referensi: pola & potongan kode di bawah diadopsi dari proyek `aviat-odoo` (PT KP3) — kasusnya identik (satu ERP custom berbasis Odoo 18, ingin 1 root app tunggal + flyout menu bertingkat) dan **sudah diverifikasi jalan** di database nyata di proyek itu.

## Scope

### 1. Tema warna
- Ganti palet warna default Odoo (ungu) jadi **lime green** sebagai warna primary — lewat override SCSS variables (`web.assets_backend`), bukan hardcode inline style.
- Dark mode: belum jadi kebutuhan, ditunda sampai ada permintaan eksplisit (tidak masuk scope awal).

### 2. Struktur menu: 1 root app tunggal (bukan multi-app switcher)
Odoo native: tiap module bisnis (`sale`, `purchase`, `stock`, `account`, `hr`, dst) jadi **app top-level sendiri-sendiri** di App Switcher (grid ikon pas klik logo/home) — App Switcher jadi ramai kalau banyak module custom.

**Keputusan**: semua module dari `app/mvp` & `app/custom` **bukan** app top-level masing-masing, melainkan jadi kategori di dalam **satu root app tunggal** (nama root: `brand_name`, mis. "ERP") — sejajar dengan app bawaan Odoo yang tetap ada (Settings, Discuss).

```
Level App (App Switcher):   <brand_name/ERP>  |  Settings  |  Discuss
                                    |
Level Kategori (dalam ERP): Sales | Purchase | Inventory | Accounting | HRIS | ...
                             (kelihatan sesuai akses group user)
```

**Implementasi (pola dari referensi)**:
1. `c18_theme` (atau addon dasar sejenis) bikin 1 `menuitem` baru **tanpa parent** — jadi root/top-level tersendiri di App Switcher, nama diambil dari `brand_name`.
2. Tiap module `app/mvp`/`app/custom` yang biasanya bikin root menu sendiri (mis. Sales, Purchase, Inventory, Accounting, HRIS) di-**reparent**: root menu module itu ditambah `parent="c18_theme.menu_erp_root"` (via `_inherit`/XML override menu, bukan ubah kode Odoo asli).
3. `depends` masing-masing module bisnis ditambah dependency ke addon yang punya root menu ini (perlu resolve xmlid-nya).
4. `'application'` di manifest module-module bisnis diubah dari `True` → `False` — karena menu-nya sekarang jadi child, bukan app top-level independen lagi. Root app satu-satunya yang `application: True` cuma addon dasar ini.

**Catatan dari pengalaman referensi**: breakdown kategori mana masuk kelompok apa (mis. apakah "Purchase" & "Inventory" jadi 1 kategori gabungan atau 2 kategori terpisah sejajar) itu keputusan per-fitur yang baru konkret saat modul `app/mvp` sungguhan dibangun — bukan sesuatu yang bisa difinalkan di `app/base` sekarang. Prinsip pentingnya: ini murni restrukturisasi `ir.ui.menu` (parent-child), bukan memecah/gabung kode module fisik.

### 3. Flyout submenu ("drill arrow") untuk menu berlapis
Odoo native: menu dengan kedalaman **3 level ke atas** (mis. `Kategori > Sub Kategori > Item`) dirender sebagai label abu-abu **mati/tidak bisa diklik** di level ke-3, anak-anaknya tampil rata (indented) di bawahnya dalam dropdown yang sama — bukan flyout bertingkat beneran.

**Keputusan**: level ke-3+ ini dibuat jadi flyout beneran — hover/klik item level ke-3 membuka submenu baru di sampingnya (kanan), dengan ikon panah (`drill arrow`) sebagai indikator item itu punya submenu.

**Implementasi (terverifikasi bisa jalan di proyek referensi)**: Odoo sendiri sudah punya infrastruktur nested `<Dropdown>` (komponen OWL) yang mendukung nested dropdown resmi (bukan workaround) — kalau `<Dropdown>` di-nest di dalam `<Dropdown>` lain, posisi default otomatis `"right-start"` (flyout ke kanan) dan hover-to-open antar sibling sudah bawaan. Jadi **tidak perlu bangun mekanisme flyout dari nol**, cukup override template `web.NavBar.SectionsMenu.Dropdown.MenuSlot` (template rekursif yang merender tiap level submenu):

```xml
<!-- Override c18_theme, ganti cabang "item punya children" -->
<Dropdown position="'right-start'">
    <button class="dropdown-item d-flex justify-content-between align-items-center" t-att-style="style">
        <span t-esc="item.name"/>
        <i class="oi oi-chevron-right ms-2"/>
    </button>
    <t t-set-slot="content">
        <t t-call="web.NavBar.SectionsMenu.Dropdown.MenuSlot">
            <t t-set="items" t-value="item.childrenTree" />
            <t t-set="decalage" t-value="20" />
        </t>
    </t>
</Dropdown>
```

Karena template ini rekursif (`t-call` ke dirinya sendiri), override berlaku otomatis di **semua** level kedalaman menu (level 3, 4, 5, dst), bukan cuma satu level tertentu.

**Icon**: `oi-chevron-right` — indikator visual standar item yang punya submenu (konvensi umum menu bertingkat, dipakai juga di proyek referensi).

**Catatan operasional penting**: perubahan ini masuk asset bundle (`web.assets_backend`), bukan `ir.ui.view`/data biasa — di proyek referensi ditemukan bahwa container Odoo yang sedang berjalan lama **tidak otomatis reload bundle** setelah module di-upgrade dari proses/container lain (mis. `docker compose run --rm`); perlu `docker restart <container_odoo>` supaya perubahan asset benar-benar kepakai. Perlu diingat saat development/deploy nanti.

### 4. Home dashboard (landing page saat app icon diklik) — dikonfirmasi & diimplementasikan 2026-08-28
**Masalah**: root app menu (`menu_erp_root`) & root kategori di bawahnya (mis. "Accounting") sengaja tanpa `action` (poin 2, murni grouping) — akibatnya webclient auto-drill ke `action` pertama yang ditemukan di pohon menu (menu dengan `sequence` terkecil, rekursif turun ke anak pertama yang punya action). Sebelum fitur ini ada, itu berarti klik icon ERP langsung membuka form **Jurnal Umum** (`c18_basic_erp`) sebagai first-impression — membingungkan.

**Keputusan**: tambah 1 menuitem baru **"Home"**, `parent="c18_theme.menu_erp_root"`, `sequence="1"` (lebih kecil dari kategori manapun), dengan `action` sendiri (`ir.actions.client`) — supaya drill berhenti di sini duluan, bukan lanjut ke action pertama modul `app/mvp`.

**Isi halaman** (client action OWL, bukan `ir.actions.act_window`, karena tidak ada model data yang perlu ditampilkan):
- Logo company aktif (`res.company.logo`)
- "Selamat Datang, {nama user login}"
- Nama company
- Teks kecil "Pilih menu di bagian atas untuk mulai bekerja."

**Sengaja generic/tanpa quick-link ke menu spesifik** (mis. tombol langsung ke Pembelian/Penjualan) — konsisten dengan prinsip di poin 2 & Struktur Modul di bawah: `c18_theme` (base layer) tidak boleh tahu menu/action milik module `app/mvp`/`app/custom`. Kalau nanti mau ada quick-link/ringkasan angka, itu ditambahkan di module `app/mvp` masing-masing (mis. `c18_basic_erp` override action `Home` ini via xmlid, atau bikin action Home sendiri lalu reparent menu), bukan di `c18_theme`.

**Struktur file** (ditambahkan ke `c18_theme/`):
```
c18_theme/
  views/
    home_dashboard_actions.xml   # ir.actions.client + menuitem "Home" (sequence=1)
  static/src/
    js/home_dashboard.js         # OWL component, registry.category("actions")
    xml/home_dashboard.xml       # template
    scss/home_dashboard.scss     # batas ukuran logo
```

## Kapan Detail Ini Terasa Konkret
Struktur kategori & kedalaman menu yang riil baru kelihatan begitu modul `app/mvp` (sales/purchases/inventory/accounting/hris) mulai dibangun — dokumen ini menyiapkan **pola teknis & keputusan strukturalnya** (1 root app, flyout otomatis di semua level), bukan daftar final kategori/menu per modul.

## Struktur Modul (rencana)
Tetap menyatu di `c18_theme` bersama branding ([01](01-branding-atribut.md)) — satu addon untuk semua hal yang sifatnya visual/framework/struktur navigasi (bukan logic bisnis):
```
c18_theme/
  views/
    erp_root_menu.xml        # menuitem root tanpa parent, nama dari brand_name
  static/src/
    scss/                     # override variabel warna (lime green)
    xml/
      menu_flyout_submenu.xml # override web.NavBar.SectionsMenu.Dropdown.MenuSlot
```
Reparent root menu tiap module bisnis (`parent="c18_theme.menu_erp_root"`, `application: False`) dilakukan **di masing-masing module `app/mvp`/`app/custom`**, bukan di `c18_theme` — sejalan dengan prinsip module dasar tidak tahu-menahu detail module turunan.
