from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _name = 'c18.sale.order'
    _description = 'Sales Order (lightweight, Basic tier)'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True, string='Number')
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    cost_center_id = fields.Many2one('c18.account.cost.center')
    note = fields.Char(string='Notes')
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
                raise UserError(_('The SO cannot be empty.'))
            rec.name = self.env.ref('c18_basic_erp.seq_c18_basic_erp_so').next_by_id()
            rec.state = 'confirmed'

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    def action_print_pdf(self):
        """Buka PDF di tab baru via /report/pdf (bukan route /report/download
        yang dipakai action manager utk ir.actions.report qweb-pdf) - route
        ini tidak set Content-Disposition, jadi browser tampilkan inline pakai
        native PDF viewer (rasio halaman A4 asli), bukan langsung men-download."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/report/pdf/c18_basic_erp.report_sale_order_document/{self.id}',
            'target': 'new',
        }


class SaleOrderLine(models.Model):
    _name = 'c18.sale.order.line'
    _description = 'Sales Order Line'
    _order = 'sequence, id'

    order_id = fields.Many2one('c18.sale.order', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('c18.product', required=True)
    qty = fields.Float(default=1.0)
    price_unit = fields.Float(string='Unit Selling Price')
    subtotal = fields.Monetary(compute='_compute_subtotal', currency_field='currency_id', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id')

    @api.depends('qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.price_unit
