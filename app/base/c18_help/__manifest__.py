{
    'name': 'ERP Help',
    'version': '18.0.1.0.0',
    'summary': 'Root menu "Help" - viewer dokumen .rst on-the-fly (prototype)',
    'description': """
Prototype: root menu top-level "Help" (setara Apps/Settings di app switcher,
sengaja TIDAK direparent ke c18_theme.menu_erp_root - beda karakter dari
module bisnis, ini utility/dokumentasi).

Ditampilkan lewat form Odoo biasa (`c18.help.guide`, field Html, 1 record per
dokumen) - bukan ir.actions.act_url (full page, keluar dari shell Odoo) -
supaya breadcrumb/sidebar/top bar tetap kelihatan. Compute method baca file
.rst dari static/docs/ (path disimpan di field `filename`) dan convert ke
HTML on-the-fly pakai `docutils` (sudah ada di image odoo:18, tidak perlu
tambah dependency seperti kalau pakai Markdown). File sumber .rst tidak
diubah/ditulis ulang - murni dibaca & di-render tiap kali form dibuka.

3 dokumen (00 Profile, 01 Transactions, 02 Procedure) - salinan RST dari
testing/mvp/*.md di root repo (sumber aslinya tetap Markdown, ini cuma
salinan buat ditampilkan di Odoo).

Requirement/PRD belum ditulis - ini spike/prototype atas permintaan user,
belum diputuskan jadi fitur permanen.
""",
    'category': 'Hidden',
    'depends': ['base', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/guide_data.xml',
        'views/guide_views.xml',
        'views/menu.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
