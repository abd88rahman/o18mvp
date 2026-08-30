{
    'name': 'ERP Accounting Foundation',
    'version': '18.0.1.0.0',
    'summary': 'Fondasi GL (CoA, Journal, Move, Cost Center) + Partner/Product tier Basic',
    'description': """
Fondasi Accounting/GL zero-dependency (tidak extend `account` bawaan Odoo):
- Chart of Accounts (`c18.account.account`) + data default 15 tipe akun ala Accurate
- Journal (`c18.account.journal`) - daftar tipe jurnal granular
- Account Move/Move Line (`c18.account.move` + `.line`) dengan generic reference
- Cost Center (`c18.account.cost.center`)
- Multi-currency: kurs transaksi di move + tabel kurs harian (`c18.account.exchange.rate`)
- Partner: extend `res.partner` (is_customer/is_vendor, NPWP, termin pembayaran)
- Product tier Basic (`c18.product`): tanpa kategori/UoM
- Kas Bank (Kas Masuk/Keluar/Transfer, `c18.account.cash`)
- PO/SO ringan (`c18.purchase.order` / `c18.sale.order`)
- Penerimaan Barang, Pembelian (`c18.purchase.receipt` / `c18.purchase.bill`)
- Pengiriman Barang, Penjualan (`c18.sale.delivery` / `c18.sale.invoice`)
- Costing Persediaan FIFO/Average (`c18.stock.layer` + field di `c18.product`)
- Uang Muka Pembelian/Penjualan (`c18.purchase.advance` / `c18.sale.advance`)
- Pembayaran Vendor/Penerimaan Piutang dengan deduction (`c18.purchase.payment` / `c18.sale.receipt`) -
  simplifikasi: deduction level header, bukan per-baris invoice seperti draft requirement asal
- Retur Barang Vendor/Customer (`c18.purchase.return` / `c18.sale.return`)
- Write-off Hutang/Piutang (`c18.purchase.writeoff` / `c18.sale.writeoff`)
- Aktiva Tetap Basic - form generik (`c18.fixed.asset.entry`)
- Payroll Basic - Jurnal Pengakuan/Pembayaran (`c18.payroll.accrual` / `c18.payroll.payment`)
- Pemakaian Sendiri & Stok Opname (`c18.stock.consume` / `c18.stock.opname`)
- Tutup Buku - Penyesuaian Awal/Akhir Tahun (reuse `c18.account.move`, tanggal terkunci
  1 Jan/31 Des) + proses Tutup Buku otomatis (`c18.account.closing`, nolkan akun Pendapatan/
  Beban ke Laba Ditahan) + penguncian periode (blokir tambah/edit/hapus jurnal di tanggal
  yang sudah ditutup)

Requirement/PRD lengkap ada di erd/mvp/01-accounting-foundation.md dan
erd/mvp/06-accounting-business.md pada root repo ini, bukan di sini.
Seluruh scope form transaksi tier Basic (poin A-K) sudah diimplementasikan.
BELUM ada: Laporan Keuangan (Neraca/Laba Rugi/Trial Balance/Buku Besar), Kartu
Stok, dan seluruh scope tier Standard+ (Aktiva Tetap otomatis, dst - lihat
erd/00-tiering-produk.md).
Belum melewati smoke test end-to-end - lihat erd/mvp/00-status-requirement.md.

Demo data untuk presentasi client: TIDAK pakai mekanisme 'demo' bawaan Odoo
(key 'demo' di manifest) - modul ini 'auto_install': True, dan modul
auto_install TERBUKTI tidak pernah kebagian flag demo dari proses instalasi
database (keterbatasan Odoo sendiri, dicek langsung ke source
odoo/modules/graph.py - bukan bug kita, tidak ada workaround praktis).
Sebagai gantinya, generate manual lewat odoo shell:
    env['c18.basic.erp.demo.generator']._generate()
    env.cr.commit()
~13 transaksi contoh (Kas Masuk/Keluar/Transfer, siklus Pembelian lengkap,
siklus Penjualan lengkap, Aktiva Tetap, Payroll), tanggal relatif ke hari
generate (bukan fixed). Idempotent - aman dipanggil ulang, tidak dobel.
Detail lengkap: erd/mvp/08-demo-data.md.
""",
    'category': 'Accounting',
    'depends': ['base', 'web', 'c18_theme'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/account_account_data.xml',
        'data/account_journal_data.xml',
        'views/account_account_views.xml',
        'views/account_journal_views.xml',
        'views/account_move_views.xml',
        'views/account_cash_views.xml',
        'views/purchase_order_report.xml',
        'views/purchase_order_views.xml',
        'views/purchase_receipt_views.xml',
        'views/purchase_bill_views.xml',
        'views/purchase_advance_views.xml',
        'views/purchase_payment_views.xml',
        'views/purchase_return_views.xml',
        'views/purchase_writeoff_views.xml',
        'views/sale_order_report.xml',
        'views/sale_order_views.xml',
        'views/sale_delivery_views.xml',
        'views/sale_invoice_report.xml',
        'views/sale_invoice_views.xml',
        'views/sale_advance_views.xml',
        'views/sale_receipt_views.xml',
        'views/sale_return_views.xml',
        'views/sale_writeoff_views.xml',
        'views/fixed_asset_views.xml',
        'views/fixed_asset_report_views.xml',
        'views/payroll_views.xml',
        'views/stock_consume_views.xml',
        'views/stock_opname_views.xml',
        'views/account_closing_views.xml',
        'views/cost_center_views.xml',
        'views/exchange_rate_views.xml',
        'views/res_partner_views.xml',
        'views/product_views.xml',
        'views/res_company_views.xml',
        'views/financial_report_actions.xml',
        'views/report_layout_extend.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'c18_basic_erp/static/src/report/trial_balance_report.js',
            'c18_basic_erp/static/src/report/trial_balance_report.xml',
            'c18_basic_erp/static/src/report/trial_balance_report.scss',
            'c18_basic_erp/static/src/report/general_ledger_report.js',
            'c18_basic_erp/static/src/report/general_ledger_report.xml',
            'c18_basic_erp/static/src/report/balance_sheet_report.js',
            'c18_basic_erp/static/src/report/balance_sheet_report.xml',
            'c18_basic_erp/static/src/report/income_statement_report.js',
            'c18_basic_erp/static/src/report/income_statement_report.xml',
            'c18_basic_erp/static/src/report/subsidiary_ledger_report.js',
            'c18_basic_erp/static/src/report/subsidiary_ledger_report.xml',
            'c18_basic_erp/static/src/report/aging_report.js',
            'c18_basic_erp/static/src/report/aging_report.xml',
            'c18_basic_erp/static/src/report/analysis_report.js',
            'c18_basic_erp/static/src/report/analysis_report.xml',
            'c18_basic_erp/static/src/report/equity_changes_report.js',
            'c18_basic_erp/static/src/report/equity_changes_report.xml',
            'c18_basic_erp/static/src/report/trial_balance_yearly_report.js',
            'c18_basic_erp/static/src/report/trial_balance_yearly_report.xml',
            'c18_basic_erp/static/src/report/trial_balance_yearly_report.scss',
            'c18_basic_erp/static/src/report/balance_sheet_yearly_report.js',
            'c18_basic_erp/static/src/report/balance_sheet_yearly_report.xml',
            'c18_basic_erp/static/src/report/income_statement_yearly_report.js',
            'c18_basic_erp/static/src/report/income_statement_yearly_report.xml',
            'c18_basic_erp/static/src/report/stock_card_report.js',
            'c18_basic_erp/static/src/report/stock_card_report.xml',
            'c18_basic_erp/static/src/report/inventory_balance_report.js',
            'c18_basic_erp/static/src/report/inventory_balance_report.xml',
            'c18_basic_erp/static/src/js/home_dashboard_patch.js',
            'c18_basic_erp/static/src/xml/home_dashboard_patch.xml',
        ],
    },
    # auto_install=True - tier Basic wajib ada begitu c18_theme ter-install
    # (satu-satunya depends non-core di atas), konsisten dengan pola
    # auto_install di c18_theme/__manifest__.py sendiri.
    'auto_install': True,
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
