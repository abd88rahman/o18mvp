# Requirement - Branding & Atribut Odoo (`c18_theme`)

Status: **requirement disusun (2026-08-25), belum diimplementasikan.**

Referensi: pola & sebagian besar temuan teknis diadopsi dari modul dengan nama sama, `c18_theme`, tapi di **repo lain** (`odoo18_accurate`, dokumen `requirements/o18-10-tema-ui.md` — di luar repo ini, cuma catatan asal-usul, bukan modul yang sama fisiknya) — sama-sama target Odoo 18 Community, jadi temuan teknisnya (server_wide_modules, static rendering database manager, dsb) berlaku sama di sini.

Tujuan: **warna, layout, dan styling tetap default Odoo** — hanya kata "Odoo" (nama), logo, favicon, dan atribut branding lain yang diganti jadi milik sendiri, tanpa mengubah struktur navigasi/framework bawaan Odoo. Bukan rewrite UI, bukan re-skin total. (Perubahan warna tema & hierarki menu ada di dokumen terpisah, lihat [02-tema-menu.md](02-tema-menu.md).)

## Scope

### 1. Title, favicon & logo
- Title tab browser, halaman login, dan Database Manager — ganti "Odoo" jadi `brand_name` custom.
- Favicon — ganti dari ikon huruf "O" ungu default Odoo.
- Logo di navbar/header backend dan halaman login — ganti dari logo Odoo default.

### 2. Hapus atribusi "Powered by Odoo"
- Footer halaman login (dan halaman yang extend template login yang sama: Reset Password, Sign up dari modul `auth_signup`).

### 3. Template Email
Dipindah ke dokumen terpisah: [04-template-email.md](04-template-email.md).

### 4. Template Report (PDF)
Dipindah ke dokumen terpisah: [05-template-report.md](05-template-report.md).

### 5. Database Manager (`/web/database/manager`)
- Ditambah gate: wajib isi Master Password dulu sebelum list database kebuka (mengikuti pola `c18_theme`, lihat detail mekanisme di dokumen referensi).
- Halaman ini juga di-reskin (title/favicon/logo/teks "Odoo").

### 6. User menu (profile icon, pojok kanan atas)
Menu dropdown user (klik icon profile) native Odoo berisi: Documentation, Support, Shortcuts, Onboarding, Preferences, My Odoo.com Account, Install App(s), Log out.

**Disisakan hanya 3**: Shortcuts, Preferences, Log out.
**Dihapus/disembunyikan**: Documentation, Support, Onboarding, My Odoo.com Account, Install App(s) — semuanya link/fitur yang mengarah ke ekosistem odoo.com atau tidak relevan untuk end user produk ini.

### 7. Discuss / Chat (menu bar horizontal atas)
Fitur chat (Discuss) tetap dipakai/diperlukan, cuma ada 2 hal bawaan yang perlu disesuaikan:
- **Hapus opsi "Install Odoo"** — tile notifikasi yang muncul di dropdown messaging menu (icon amplop di navbar atas), **bukan** pesan chat asli dari OdooBot. Sumbernya sudah diriset ke source Odoo 18 (`addons/mail/static/src/core/web/messaging_menu_patch.js`, getter `installationRequest`) — ini adalah item sintetis yang dirender JS di daftar preview chat (disisipkan di antara thread asli), dipicu kalau `canPromptToInstall` (dari `this.pwa.canPromptToInstall`, terkait prompt install PWA) bernilai true, pakai avatar OdooBot sebagai icon tapi bukan hasil kirim pesan. Cara hilangkan: patch JS (`patch()`) pada getter `canPromptToInstall`/`installationRequest.isShown` di komponen ini supaya selalu `false`, tidak perlu sentuh data OdooBot/channel general sama sekali.
- **Ganti nama "OdooBot" jadi "System Bot"** — di semua tempat nama itu muncul (daftar chat, pesan, avatar/label), termasuk pesan pertama di channel "general" yang defaultnya dikirim oleh OdooBot.

## Konfigurasi (rencana, mengikuti pola referensi)

Brand name/logo/favicon dibaca dari `odoo.conf`, bukan hardcode:

```ini
[options]
brand_name = <diisi user langsung di file konfigurasi>
brand_logo = logo_custom.png
brand_favicon = favicon_custom.png
```

`brand_name` **tidak ditentukan di dokumen requirement ini** — user yang akan mengisi langsung di `app/docker/etc/odoo.conf` saat deploy (bukan hardcode di kode `c18_theme`), jadi modul cukup baca via `config.get('brand_name', 'Odoo')`.

## Catatan Teknis Penting (dari pengalaman implementasi di repo referensi)

1. **`server_wide_modules`**: route nodb (`/web/login`, `/web/database/manager`) hanya memuat controller dari modul yang terdaftar di `server_wide_modules`, bukan dari modul yang ter-install di database. Modul branding ini **wajib** ditambahkan ke `server_wide_modules` di `odoo.conf`, kalau tidak override controller Database Manager tidak akan pernah aktif.
2. **Halaman gate Database Manager tidak bisa** dibuat sebagai `ir.ui.view` (QWeb via ORM) karena di level nodb `request.env` belum tentu ada database yang ter-resolve. Harus dirender dari file statis via `qweb_render()` standalone, sama seperti cara Odoo merender `database_manager.qweb.html` bawaan.
3. Sisi client (OWL/JS) tidak bisa baca `odoo.conf` langsung — brand info perlu diselipkan lewat `session_info` (override `ir.http._get_session_info()`) supaya JS/OWL bisa akses `session.brand_name`.
4. `brand_logo`/`brand_favicon` cuma nama file, file fisiknya ditaruh manual di `static/src/img/<nama_file>`. Kalau file tidak ada, fallback ke default Odoo (tidak error).

## Struktur Modul (rencana)
```
c18_theme/
  __manifest__.py        # depends: ['web', 'auth_signup', 'mail', 'portal'] - mail/portal
                          # ditambah utk override template email (lihat 04)
  __init__.py
  controllers/
    __init__.py
    database.py          # override Database controller: gate password
  models/
    ir_http.py            # expose brand_* ke session_info
  static/src/img/         # logo, favicon custom - filenya sudah ada (placeholder):
                          # logo_custom.png, favicon_custom.png, favicon_custom_32.png
  static/src/js/          # patch user menu (hapus item Documentation/Support/dsb)
  views/
    webclient_templates.xml         # login, login_layout, title
    database_manager_templates.xml  # override db manager + form gate password
  data/
    res_partner_data.xml    # rename OdooBot -> System Bot (mail.partner_root, noupdate)
```
Override template email ([04](04-template-email.md)) & report ([05](05-template-report.md)) direncanakan sebagai bagian modul ini juga, detail struktur menyusul di masing-masing dokumen.

## Belum Diputuskan / Perlu Riset Lanjutan
- [ ] Pengecekan tempat lain yang mungkin hardcode string "OdooBot" (di luar field `name` record `res.partner`) — dicek saat implementasi rename ke "System Bot".
