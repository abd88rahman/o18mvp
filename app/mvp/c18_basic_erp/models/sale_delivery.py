from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleDelivery(models.Model):
    _name = 'c18.sale.delivery'
    _description = 'Pengiriman Barang'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    so_ref_id = fields.Many2one('c18.sale.order', string='SO', domain=[('state', '=', 'confirmed')])
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    cost_center_id = fields.Many2one('c18.account.cost.center')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many('c18.sale.delivery.line', 'delivery_id', copy=True)
    amount_total = fields.Monetary(compute='_compute_amount_total', currency_field='currency_id', store=True,
                                    help='Nilai HPP (cost), bukan harga jual - dihitung saat posting dari costing engine.')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.depends('line_ids.cost_amount')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('cost_amount'))

    @api.onchange('so_ref_id')
    def _onchange_so_ref_id(self):
        if self.so_ref_id:
            self.partner_id = self.so_ref_id.partner_id
            self.line_ids = [(5, 0, 0)] + [(0, 0, {
                'so_line_id': line.id,
                'product_id': line.product_id.id,
                'qty_delivered': line.qty,
            }) for line in self.so_ref_id.line_ids if line.product_id.product_type == 'barang_stok']

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
                raise UserError(_('Pengiriman Barang tidak boleh kosong.'))
            for line in rec.line_ids:
                if line.product_id.product_type != 'barang_stok':
                    raise UserError(_('Pengiriman Barang cuma relevan utk produk tipe Barang Stok.'))
                line.cost_amount = line.product_id._stock_consume(line.qty_delivered)
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_pngb').id,
                'date': rec.date,
                'ref': rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_5_1000').id,
                        'debit': rec.amount_total,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_1_1300').id,
                        'credit': rec.amount_total,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ],
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})

    def action_reset_to_draft(self):
        raise UserError(_('Pengiriman Barang yang sudah posted tidak bisa dibatalkan (mempengaruhi Persediaan) - buat dokumen koreksi terpisah.'))


class SaleDeliveryLine(models.Model):
    _name = 'c18.sale.delivery.line'
    _description = 'Pengiriman Barang Line'
    _order = 'sequence, id'

    delivery_id = fields.Many2one('c18.sale.delivery', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    so_line_id = fields.Many2one('c18.sale.order.line')
    product_id = fields.Many2one('c18.product', required=True)
    qty_delivered = fields.Float(default=1.0)
    cost_amount = fields.Monetary(currency_field='currency_id', readonly=True,
                                   help='HPP hasil konsumsi stok saat posting (FIFO layer / avg_cost).')
    currency_id = fields.Many2one(related='delivery_id.currency_id')
