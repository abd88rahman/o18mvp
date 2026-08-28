from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseBill(models.Model):
    _name = 'c18.purchase.bill'
    _description = 'Pembelian (Vendor Bill)'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    po_ref_id = fields.Many2one('c18.purchase.order', string='PO')
    grni_ref_id = fields.Many2one('c18.purchase.receipt', string='Penerimaan Barang',
                                   help='Diisi = tutup GRNI (debit otomatis Hutang Belum Difaktur). Kosong = debit bebas dipilih user.')
    debit_account_id = fields.Many2one('c18.account.account', string='Akun Debit',
                                        help='Wajib diisi kalau tidak referensi GRNI (mis. Beban/Persediaan langsung).')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many('c18.purchase.bill.line', 'bill_id', copy=True)
    amount_total = fields.Monetary(compute='_compute_amount_total', currency_field='currency_id', store=True)
    amount_paid = fields.Monetary(default=0.0, currency_field='currency_id', copy=False,
                                   help='Total sudah dibayar via Pembayaran Vendor - diupdate dari sana.')
    amount_residual = fields.Monetary(compute='_compute_amount_residual', currency_field='currency_id', store=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('subtotal'))

    @api.depends('amount_total', 'amount_paid')
    def _compute_amount_residual(self):
        for rec in self:
            rec.amount_residual = rec.amount_total - rec.amount_paid

    @api.onchange('grni_ref_id')
    def _onchange_grni_ref_id(self):
        if self.grni_ref_id:
            self.partner_id = self.grni_ref_id.partner_id
            self.po_ref_id = self.grni_ref_id.po_ref_id
            self.debit_account_id = self.env.ref('c18_basic_erp.acc_2_1100')
            self.line_ids = [(5, 0, 0)] + [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'qty': line.qty_received,
                'price_unit': line.price_unit,
            }) for line in self.grni_ref_id.line_ids]

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.name == 'New':
                rec.name = f'draft-{rec.id}'
        return records

    def action_post(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            if not rec.line_ids:
                raise UserError(_('Pembelian tidak boleh kosong.'))
            if rec.grni_ref_id:
                debit_account = self.env.ref('c18_basic_erp.acc_2_1100')
            else:
                if not rec.debit_account_id:
                    raise UserError(_('Akun Debit wajib diisi kalau tidak referensi Penerimaan Barang (GRNI).'))
                debit_account = rec.debit_account_id
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_pb').id,
                'date': rec.date,
                'ref': rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': debit_account.id,
                        'debit': rec.amount_total,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_2_1000').id,
                        'credit': rec.amount_total,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ],
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})


class PurchaseBillLine(models.Model):
    _name = 'c18.purchase.bill.line'
    _description = 'Pembelian Line'
    _order = 'sequence, id'

    bill_id = fields.Many2one('c18.purchase.bill', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('c18.product')
    name = fields.Char(string='Keterangan')
    qty = fields.Float(default=1.0)
    price_unit = fields.Float(string='Harga Satuan')
    subtotal = fields.Monetary(compute='_compute_subtotal', currency_field='currency_id', store=True)
    currency_id = fields.Many2one(related='bill_id.currency_id')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and not self.name:
            self.name = self.product_id.name

    @api.depends('qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.price_unit
