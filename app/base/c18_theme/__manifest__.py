{
    'name': 'ERP Base Theme',
    'version': '18.0.1.0.0',
    'summary': 'Branding, tema warna, dan struktur menu dasar ERP (bukan Odoo default)',
    'description': """
Modul dasar yang menampung semua modifikasi level framework/branding Odoo:
- Branding & atribut (icon, logo, favicon, hapus "Powered by Odoo", dsb)
- Tema warna & hierarki menu (1 root app + flyout submenu)
- Template email & report

Requirement/PRD lengkap ada di erd/base/ (01-05) pada root repo ini, bukan di sini.
Belum melewati smoke test end-to-end - lihat erd/base/00-status-requirement.md.
""",
    'category': 'Hidden',
    'depends': ['web', 'auth_signup', 'mail', 'portal'],
    'data': [
        'views/webclient_templates.xml',
        'views/erp_root_menu.xml',
        'views/ir_module_module_views.xml',
        'data/res_partner_data.xml',
        'data/mail_templates_email_layouts.xml',
        'data/res_company_data.xml',
    ],
    'assets': {
        # colors.scss wajib masuk bundle _assets_primary_variables dan dimuat
        # SEBELUM primary_variables.scss (nilai $o-brand-primary di sana
        # pakai !default) - lihat komentar di colors.scss.
        'web._assets_primary_variables': [
            ('before', 'web/static/src/scss/primary_variables.scss', 'c18_theme/static/src/scss/colors.scss'),
        ],
        'web.assets_backend': [
            'c18_theme/static/src/xml/menu_flyout_submenu.xml',
            'c18_theme/static/src/js/user_menu_patch.js',
            'c18_theme/static/src/js/messaging_menu_patch.js',
        ],
    },
    # auto_install=True (bukan list parsial ['web']) - dicek langsung: di
    # database baru, keempat depends (web/auth_signup/mail/portal) semuanya
    # sudah ter-install by default lewat auto_install chain modul Odoo
    # sendiri, jadi trigger penuh ini aman & terbukti jalan (2026-08-27).
    'auto_install': True,
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
