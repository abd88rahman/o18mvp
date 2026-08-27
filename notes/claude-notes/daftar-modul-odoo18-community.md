# Daftar Addon Odoo 18 Community (Image Resmi `odoo:18`)

Digenerate langsung dari source Odoo 18 Community (`odoo18_original/addons/`, di luar repo ini — cocok dengan yang dipakai image resmi `odoo:18` di Docker Hub). **Bukan** daftar model/tabel per fitur seperti [`notes/human-notes/modul-asli-odoo.txt`](../human-notes/modul-asli-odoo.txt) — ini daftar **addon/app**, tujuannya supaya jelas apa yang genuinely tersedia vs yang harus dibangun sendiri dari nol, sesuai konvensi "zero dependency ke app bisnis bawaan Odoo" di [`erd/00-konvensi-teknis.md`](../../erd/00-konvensi-teknis.md).

Status: generate 2026-08-26. Catatan versi: image `odoo:18` di Docker Hub itu tag mengambang (terus dapat patch), jadi daftar ini bisa sedikit beda dari yang benar-benar ke-pull nanti — tapi nama/struktur addon inti tidak akan berubah drastis dalam rentang bulan.

## Framework / Inti (dipakai `c18_theme` & wajib ada di setiap install)
`base`, `web`, `mail`, `bus`, `portal`, `auth_signup`, `auth_password_policy*`, `auth_totp*`, `barcodes`, `board`, `calendar`, `digest`, `iap`, `onboarding`, `resource`, `sms`, `utm`, `uom`, `rating`, `phone_validation`

## Accounting (`account_*`) — 20 addon
`account` (inti), `account_check_printing`, `account_debit_note`, `account_edi*`, `account_fleet`, `account_payment`, `account_peppol`, `account_qr_code_emv`, `account_qr_code_sepa`, `account_tax_python`, dst. Plus `analytic` (dasar fitur Analytic Accounting yang di repo ini diganti istilah "Cost Center", lihat [erd/00-konvensi-teknis.md](../../erd/00-konvensi-teknis.md) poin 5).

## Sales (`sale`, `sale_*`) — ~30 addon
`sale` (inti), `sale_management`, `sale_stock`, `sale_mrp`, `sale_project`, `sale_timesheet`, `sale_margin`, `sale_expense`, `sale_purchase`, `sale_crm`, `sale_loyalty`, dst.

## Purchase (`purchase`, `purchase_*`) — 8 addon
`purchase` (inti — PR/PO/Receive/Invoice/Return), `purchase_stock`, `purchase_mrp`, `purchase_repair`, `purchase_requisition*` (Purchase Agreements), `purchase_product_matrix`, `purchase_edi_ubl_bis3`.

## Inventory / Stock (`stock`, `stock_*`) — 9 addon
`stock` (inti), `stock_account`, `stock_delivery`, `stock_landed_costs`, `stock_picking_batch`, `stock_dropshipping`, `stock_fleet`, `stock_sms`.

## Manufacturing (`mrp`, `mrp_*`) — 10 addon
`mrp` (inti), `mrp_account`, `mrp_landed_costs`, `mrp_product_expiry`, `mrp_repair`, `mrp_subcontracting*` (5 varian).

## HR (`hr`, `hr_*`) — ~25 addon
`hr` (inti — Employee/Department/Job/Contract), `hr_attendance`, `hr_contract`, `hr_expense`, `hr_holidays` (Time Off), `hr_recruitment*`, `hr_skills*`, `hr_timesheet*`, `hr_work_entry*`, `hr_org_chart`, `hr_fleet`, `hr_maintenance`, dst.

## CRM & Project
`crm` + turunannya (`crm_iap_*`, `crm_livechat`, `crm_sms`, dst), `project` + turunannya (`project_account`, `project_mrp`, `project_purchase`, `project_stock`, `project_timesheet_holidays`, `project_todo`, dst).

## Point of Sale (`point_of_sale`, `pos_*`) — ~40 addon
`point_of_sale` (inti), `pos_restaurant`, `pos_self_order*`, `pos_hr`, `pos_discount`, `pos_loyalty`, `pos_sale`, `pos_mrp`, plus banyak integrasi pembayaran (`pos_adyen`, `pos_stripe`, `pos_razorpay`, dst).

## Website / eCommerce (`website`, `website_*`) — ~60 addon
`website` (inti), `website_sale` (eCommerce), `website_event*`, `website_slides*` (eLearning), `website_forum`, `website_blog`, `website_livechat`, `website_crm*`, `website_membership`, dst.

## Product & Umum
`product`, `product_expiry`, `product_margin`, `product_matrix`, `product_images`, `delivery*`, `repair`, `fleet`, `maintenance`, `event*`, `survey`, `membership`, `lunch`, `gamification*`, `mass_mailing*`, `spreadsheet*` (termasuk `spreadsheet_dashboard*`), `im_livechat`, `social_media`.

## Payment Gateway (`payment_*`, integrasi pihak ketiga)
`payment` (inti) + ~15 provider: `payment_stripe`, `payment_paypal`, `payment_mollie`, `payment_razorpay`, `payment_adyen`, `payment_authorize`, dst.

## Lokalisasi (`l10n_*`) — ~150+ addon
1 addon per negara/region (`l10n_id` Indonesia, `l10n_us`, `l10n_uk`, `l10n_sg`, dst) + varian pajak/e-invoicing spesifik negara (`l10n_id_efaktur`, `l10n_my_edi`, dst). Tidak dirinci satu-satu di sini — cek `l10n_id*` kalau butuh referensi pajak Indonesia (PPN/e-Faktur) meski kita tidak depends langsung ke situ (prinsip zero dependency).

## Testing (`test_*`)
Addon internal buat testing framework Odoo sendiri (`test_mail`, `test_website`, dst) — tidak relevan buat kita, bukan fitur bisnis.

---
**Cara update daftar ini**: `ls <source-odoo-18>/addons` diregenerate ulang kalau butuh verifikasi terbaru (source lokal `odoo18_original` bisa jadi sudah beberapa bulan tertinggal dari image Docker yang benar-benar dipakai — lihat catatan di [rencana-pengembangan.md](rencana-pengembangan.md)).
