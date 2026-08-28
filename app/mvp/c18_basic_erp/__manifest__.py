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
- Costing Persediaan FIFO/Average (`c18.account.stock.layer` + field di `c18.product`)
- Uang Muka Pembelian/Penjualan (`c18.purchase.advance` / `c18.sale.advance`)
- Pembayaran Vendor/Penerimaan Piutang dengan deduction (`c18.purchase.payment` / `c18.sale.receipt`) -
  simplifikasi: deduction level header, bukan per-baris invoice seperti draft requirement asal
- Retur Barang Vendor/Customer (`c18.purchase.return` / `c18.sale.return`)
- Write-off Hutang/Piutang (`c18.purchase.writeoff` / `c18.sale.writeoff`)
- Aktiva Tetap Basic - form generik (`c18.fixed.asset.entry`)
- Payroll Basic - Jurnal Pengakuan/Pembayaran (`c18.payroll.accrual` / `c18.payroll.payment`)
- Pemakaian Sendiri & Stok Opname (`c18.account.stock.consume` / `c18.account.stock.opname`)
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
        'views/purchase_order_views.xml',
        'views/purchase_receipt_views.xml',
        'views/purchase_bill_views.xml',
        'views/purchase_advance_views.xml',
        'views/purchase_payment_views.xml',
        'views/purchase_return_views.xml',
        'views/purchase_writeoff_views.xml',
        'views/sale_order_views.xml',
        'views/sale_delivery_views.xml',
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
        'views/menu.xml',
    ],
    # auto_install=True - tier Basic wajib ada begitu c18_theme ter-install
    # (satu-satunya depends non-core di atas), konsisten dengan pola
    # auto_install di c18_theme/__manifest__.py sendiri.
    'auto_install': True,
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
