from datetime import timedelta

from odoo import api, fields, models


class DemoGenerator(models.TransientModel):
    _name = 'c18.basic.erp.demo.generator'
    _description = 'Demo Data Generator (dipanggil sekali oleh demo/demo_data.xml)'

    @api.model
    def _generate(self):
        """Bikin ~13 transaksi contoh (Kas Bank, siklus Pembelian, siklus Penjualan,
        Aktiva Tetap, Payroll) buat presentasi ke calon client - subset representatif,
        BUKAN skenario lengkap (beda dari testing/mvp/*.md). Tanggal relatif ke hari ini
        (bukan tanggal fixed) supaya masuk akal kapan pun demo di-load. Idempotent lewat
        ir.config_parameter guard - <function> di file demo bisa terpanggil ulang tiap
        module update, jangan sampai data dobel."""
        param = self.env['ir.config_parameter'].sudo()
        if param.get_param('c18_basic_erp.demo_generated'):
            return
        today = fields.Date.context_today(self)

        vendor = self.env['res.partner'].create({
            'name': 'PT Ban Nusantara Distribusi', 'is_vendor': True, 'company_type': 'company',
        })
        customer = self.env['res.partner'].create({
            'name': 'Toko Ban Makmur', 'is_customer': True, 'company_type': 'company',
        })
        employee = self.env['res.partner'].create({'name': 'Budi Santoso'})

        product = self.env['c18.product'].create({
            'code': 'BAN-A1', 'name': 'Ban Merk A Tipe 1', 'product_type': 'barang_stok',
        })

        kas = self.env.ref('c18_basic_erp.acc_1_1000')
        bank = self.env.ref('c18_basic_erp.acc_1_1100')

        # 1. Kas Masuk - pendapatan lain-lain
        cash_in = self.env['c18.account.cash'].create({
            'journal_id': self.env.ref('c18_basic_erp.journal_km').id,
            'date': today - timedelta(days=14),
            'account_id': kas.id,
            'note': 'Sewa gudang bulan ini',
            'line_ids': [(0, 0, {
                'account_id': self.env.ref('c18_basic_erp.acc_8_1000').id,
                'amount': 500000, 'name': 'Sewa gudang',
            })],
        })
        cash_in.action_post()

        # 2. Kas Keluar - beli ATK
        cash_out = self.env['c18.account.cash'].create({
            'journal_id': self.env.ref('c18_basic_erp.journal_kk').id,
            'date': today - timedelta(days=13),
            'account_id': kas.id,
            'note': 'Beli ATK kantor',
            'line_ids': [(0, 0, {
                'account_id': self.env.ref('c18_basic_erp.acc_6_1100').id,
                'amount': 250000, 'name': 'ATK',
            })],
        })
        cash_out.action_post()

        # 3. Transfer Kas -> Bank
        transfer = self.env['c18.account.cash'].create({
            'journal_id': self.env.ref('c18_basic_erp.journal_trf').id,
            'date': today - timedelta(days=12),
            'account_id': kas.id,
            'account_id_dest': bank.id,
            'amount': 5000000,
            'note': 'Setor kas ke bank',
        })
        transfer.action_post()

        # 4-6. Siklus Pembelian: PO -> Penerimaan Barang -> Pembelian (Vendor Bill)
        po = self.env['c18.purchase.order'].create({
            'partner_id': vendor.id,
            'date': today - timedelta(days=10),
            'line_ids': [(0, 0, {'product_id': product.id, 'qty': 20, 'price_unit': 700000})],
        })
        po.action_confirm()

        receipt = self.env['c18.purchase.receipt'].create({
            'po_ref_id': po.id,
            'partner_id': vendor.id,
            'date': today - timedelta(days=9),
            'line_ids': [(0, 0, {
                'po_line_id': line.id, 'product_id': line.product_id.id,
                'qty_received': line.qty, 'price_unit': line.price_unit,
            }) for line in po.line_ids],
        })
        receipt.action_post()

        bill_action = receipt.action_create_bill()
        bill = self.env['c18.purchase.bill'].browse(bill_action['res_id'])
        bill.date = today - timedelta(days=9)
        bill.action_post()

        # 7-9. Siklus Penjualan: SO -> Delivery -> Invoice (Customer Invoice)
        so = self.env['c18.sale.order'].create({
            'partner_id': customer.id,
            'date': today - timedelta(days=8),
            'line_ids': [(0, 0, {'product_id': product.id, 'qty': 10, 'price_unit': 850000})],
        })
        so.action_confirm()

        delivery = self.env['c18.sale.delivery'].create({
            'so_ref_id': so.id,
            'partner_id': customer.id,
            'date': today - timedelta(days=7),
            'line_ids': [(0, 0, {
                'so_line_id': line.id, 'product_id': line.product_id.id, 'qty_delivered': line.qty,
            }) for line in so.line_ids if line.product_id.product_type == 'barang_stok'],
        })
        delivery.action_post()

        invoice = self.env['c18.sale.invoice'].create({
            'partner_id': customer.id,
            'so_ref_id': so.id,
            'delivery_ref_id': delivery.id,
            'date': today - timedelta(days=7),
            'credit_account_id': self.env.ref('c18_basic_erp.acc_4_1000').id,
            'line_ids': [(0, 0, {
                'product_id': line.product_id.id, 'name': line.product_id.name,
                'qty': line.qty, 'price_unit': line.price_unit,
            }) for line in so.line_ids],
        })
        invoice.action_post()

        # 10. Aktiva Tetap - Acquisition
        tag = self.env['c18.fixed.asset.tag'].create({'code': 'DEMO-01', 'name': 'Printer Kantor'})
        fixed_asset = self.env['c18.fixed.asset.entry'].create({
            'transaction_type': 'pengakuan',
            'date': today - timedelta(days=5),
            'asset_tag_id': tag.id,
            'debit_account_id': self.env.ref('c18_basic_erp.acc_1_2300').id,
            'credit_account_id': bank.id,
            'amount': 15000000,
            'note': 'Beli printer kantor',
        })
        fixed_asset.action_post()

        # 11-12. Payroll - Accrual + Payment
        accrual = self.env['c18.payroll.accrual'].create({
            'date': today - timedelta(days=3),
            'partner_id': employee.id,
            'amount': 6000000,
            'note': 'Gaji bulan ini',
        })
        accrual.action_post()
        payment = self.env['c18.payroll.payment'].create({
            'date': today - timedelta(days=1),
            'partner_id': employee.id,
            'account_id': bank.id,
            'line_ids': [(0, 0, {'accrual_id': accrual.id, 'amount_paid': accrual.amount_residual})],
        })
        payment.action_post()

        param.set_param('c18_basic_erp.demo_generated', 'true')
