from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _name = 'c18.sale.order'
    _description = 'Sales Order (ringan, tier Basic)'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    cost_center_id = fields.Many2one('c18.account.cost.center')
    note = fields.Char(string='Keterangan')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many('c18.sale.order.line', 'order_id', copy=True)
    amount_total = fields.Monetary(compute='_compute_amount_total', currency_field='currency_id', store=True)
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], default='draft', copy=False, required=True)

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('subtotal'))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.name == 'New':
                rec.name = f'draft-{rec.id}'
        return records

    def action_confirm(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            if not rec.line_ids:
                raise UserError(_('SO tidak boleh kosong.'))
            rec.name = self.env.ref('c18_basic_erp.seq_c18_basic_erp_so').next_by_id()
            rec.state = 'confirmed'

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})


class SaleOrderLine(models.Model):
    _name = 'c18.sale.order.line'
    _description = 'Sales Order Line'
    _order = 'sequence, id'

    order_id = fields.Many2one('c18.sale.order', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('c18.product', required=True)
    qty = fields.Float(default=1.0)
    price_unit = fields.Float(string='Harga Jual Satuan')
    subtotal = fields.Monetary(compute='_compute_subtotal', currency_field='currency_id', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id')

    @api.depends('qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.price_unit
