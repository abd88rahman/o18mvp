{
    'name': 'ERP QA Guide',
    'version': '18.0.1.0.0',
    'summary': 'Root menu "QA Guide" - viewer dokumen .rst on-the-fly, PANDUAN TESTING INTERNAL',
    'description': """
Root menu top-level "QA Guide" (setara Apps/Settings di app switcher,
sengaja TIDAK direparent ke c18_theme.menu_erp_root - beda karakter dari
module bisnis, ini utility/dokumentasi internal).

PENTING - INTERNAL ONLY: isi modul ini panduan testing/QA (checkpoint,
istilah verifikasi, skenario perusahaan fiktif) untuk tester internal,
BUKAN dokumentasi/tutorial untuk client/end-user. Tidak ada pembatasan hak
akses di modul ini - JANGAN install modul ini di database demo atau
database yang diakses client. Requirement lengkap & alasan keputusan ini
ada di erd/base/06-qa-guide-viewer.md.

Ditampilkan lewat form Odoo biasa (`c18.help.guide`, field Html, 1 record per
dokumen) - bukan ir.actions.act_url (full page, keluar dari shell Odoo) -
supaya breadcrumb/sidebar/top bar tetap kelihatan. Compute method baca file
.rst dari static/docs/ (path disimpan di field `filename`) dan convert ke
HTML on-the-fly pakai `docutils` (sudah ada di image odoo:18, tidak perlu
tambah dependency seperti kalau pakai Markdown). File sumber .rst tidak
diubah/ditulis ulang - murni dibaca & di-render tiap kali form dibuka.

3 dokumen (00 Profile, 01 Transactions, 02 Procedure) - salinan RST dari
testing/mvp/*.md di root repo (sumber aslinya tetap Markdown, ini cuma
salinan buat ditampilkan di Odoo, disinkronkan manual - lihat catatan
"Cara Sinkronisasi .rst" di erd/base/06-qa-guide-viewer.md).

Status: PERMANEN (diputuskan 2026-08-30, sebelumnya prototype) - scope
internal tester/QA saja, bukan bagian produk yang dijual ke client.
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
