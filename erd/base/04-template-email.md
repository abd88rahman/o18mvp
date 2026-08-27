# Requirement - Template Email

Status: **draft awal hasil riset source Odoo 18 (2026-08-25), belum direview user, belum diimplementasikan.**

Dipecah dari [01-branding-atribut.md](01-branding-atribut.md) poin 3, sesuai permintaan agar direview terpisah.

## Temuan dari source Odoo 18 (`odoo18_original/addons/`)

Hampir semua email transaksional Odoo tidak menghardcode "Powered by Odoo" satu-satu di tiap `mail.template`, melainkan **mewarisi dari 1 dari 2 template layout dasar** di `addons/mail/data/mail_templates_email_layouts.xml`:

| Template ID | Baris "Powered by Odoo" | Dipakai oleh |
|---|---|---|
| `mail.mail_notification_layout` | baris 86 | Layout lengkap (header judul + body + footer) — dipakai default untuk notifikasi diskusi/chatter di banyak model. |
| `mail.mail_notification_light` | baris 160 | Layout ringkas (tanpa header judul) — dipakai untuk email transaksional model bisnis (invoice, dsb). |

**Implikasi penting**: override 2 template ini saja kemungkinan besar sudah menghilangkan "Powered by Odoo" dari **mayoritas** email transaksional sekaligus (invoice, notifikasi chatter, dll), tanpa perlu override tiap `mail.template` satu-satu — karena mereka semua pakai layout yang sama sebagai wrapper.

## Template lain yang punya teks branding sendiri (di luar 2 layout dasar)
Hasil grep `"Powered by"` ke seluruh `addons/`, disaring yang relevan ke scope `app/mvp` (sales/purchases/inventory/accounting/hris) atau ke alur akun/login:

| File | Modul | Relevan MVP? |
|---|---|---|
| `auth_signup/data/mail_template_data.xml`, `auth_signup/views/auth_signup_templates_email.xml` | Invite user, reset password | Ya — dipakai alur login/akun. |
| `portal/data/mail_template_data.xml` | Portal access | **Ya** — dipakai. |
| `hr_expense/data/mail_templates.xml` | HR Expense | **Tidak dipakai.** Dikonfirmasi lewat grep manifest ke seluruh source: `hr_expense` tidak jadi dependency modul HR/HRIS inti manapun (`hr`, `hr_contract`, `hr_payroll`, `hr_holidays`) — yang depend ke `hr_expense` cuma `project_hr_expense`, `sale_expense`, `l10n_fr_account`. Jadi tidak akan ikut ter-install otomatis; diabaikan dari scope ini. |
| `web/views/webclient_templates.xml` | Halaman login web | Sudah masuk scope [01-branding-atribut.md](01-branding-atribut.md) poin 2. |
| `im_livechat/*` | Livechat | Di luar scope MVP (kecuali nanti dipakai). |
| `crm/`, `mass_mailing*/`, `gamification/`, `lunch/`, `website_slides/`, `website_crm_partner_assign/`, `website_profile/` | Modul demo/marketing/website | Di luar scope MVP saat ini — diabaikan sampai ada kebutuhan. |
| `point_of_sale/static/.../order_receipt.xml`, `customer_display.xml` | Struk POS | Di luar scope MVP (POS belum ada di daftar `app/mvp`). |

## Rencana Implementasi
1. Override `mail.mail_notification_layout` dan `mail.mail_notification_light` — ganti blok "Powered by Odoo" jadi "Powered by `<brand_name>`" (bukan dihapus total), `brand_name` dibaca dari config yang sama seperti [01-branding-atribut.md](01-branding-atribut.md).
2. Override template `auth_signup` yang relevan.
3. Override template `portal`.
4. `hr_expense` **dikeluarkan dari scope** — tidak dipakai di `app/mvp` dan tidak auto-terinstall lewat modul HR manapun (lihat tabel di atas).
