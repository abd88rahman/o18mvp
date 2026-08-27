# Requirement - Template Report (PDF)

Status: **draft awal hasil riset source Odoo 18 (2026-08-25), belum direview user, belum diimplementasikan.**

Dipecah dari [01-branding-atribut.md](01-branding-atribut.md) poin 4, sesuai permintaan agar direview terpisah.

## Temuan dari source Odoo 18 (`addons/web/views/report_templates.xml`)

Semua layout laporan PDF bawaan (`external_layout_standard`, `external_layout_boxed`, `external_layout_bold`, `external_layout_folder`, `external_layout_wave`, `external_layout_bubble`, dst — pilihan layout yang ada di Settings > General Settings > Companies) **tidak menghardcode logo/teks "Odoo" di manapun**. Semua elemen header/footer-nya ditarik dari data `res.company`:

- Logo → `company.logo`
- Alamat/kontak perusahaan → `company.partner_id` (widget contact)
- Detail perusahaan (NPWP dsb) → `company.company_details`
- Footer bebas teks → `company.report_footer`

**Kesimpulan sementara**: branding report PDF kemungkinan **tidak perlu override kode sama sekali** — cukup diselesaikan lewat konfigurasi data `res.company` (upload logo perusahaan, isi `company_details`, isi `report_footer`) saat setup awal database/tenant. Ini beda dengan Template Email ([04](04-template-email.md)) yang memang menghardcode "Powered by Odoo" di kode templatenya.

## Yang Masih Perlu Dicek
- Judul dokumen (`<title>`) fallback ke teks `"Odoo Report"` di `web/views/report_templates.xml` — tapi ini teks `<title>` HTML (tab judul saat preview), **tidak muncul di PDF hasil cetak**, jadi prioritas rendah/optional.
- Perlu smoke test cetak invoice/laporan asli dengan `res.company` yang sudah diisi custom, untuk konfirmasi memang sudah tidak ada sisa elemen "Odoo" yang lolos.

## Rencana Implementasi
- Tidak butuh override kode untuk layout report itu sendiri — pemilihan `external_report_layout_id` (standard/boxed/bold/folder/wave/bubble) aman dipilih bebas karena keenamnya sama-sama narik dari `res.company`, tidak ada yang hardcode "Odoo". Ini murni preferensi visual, diputuskan belakangan saat setup tampilan.
- Data `res.company` (nama perusahaan, alamat, NPWP/`company_details`, `report_footer`) **beda sifat** dengan `brand_name`/logo/favicon aplikasi di [01-branding-atribut.md](01-branding-atribut.md): itu identitas aplikasi (sama untuk semua tenant di server, cocok di `odoo.conf`), sedangkan `res.company` adalah **data per perusahaan** — bahkan 1 database Odoo bisa multi-company dengan data beda-beda. Jadi **tidak dikaitkan ke `odoo.conf`/`post_init_hook`**. Cukup:
  - Placeholder values langsung di data XML `c18_theme` (`noupdate="0"`, hardcode teks polos, mis. "PT Contoh"), supaya tenant baru tidak kosong melompong saat pertama kali dibuka.
  - Admin tetap bisa (dan wajar) mengedit lagi lewat **Settings > General Settings > Companies** setelah install — workflow native Odoo, tidak perlu kode tambahan buat itu.
- Override kode baru (di luar ini) diperlukan **hanya kalau** hasil smoke test cetak menemukan elemen "Odoo" tersisa yang tidak tertutup field `res.company` di atas.
