from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleInvoice(models.Model):
    _name = 'c18.sale.invoice'
    _description = 'Customer Invoice'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True, string='Number')
    date = fields.Date(required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    so_ref_id = fields.Many2one('c18.sale.order', string='SO')
    delivery_ref_id = fields.Many2one('c18.sale.delivery', string='Delivery',
                                       help='Optional, only used to auto-fill lines & the audit trail - does not change the credit account.')
    credit_account_id = fields.Many2one('c18.account.account', string='Revenue Account', required=True)
    cost_center_id = fields.Many2one('c18.account.cost.center')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many('c18.sale.invoice.line', 'invoice_id', copy=True)
    amount_total = fields.Monetary(compute='_compute_amount_total', currency_field='currency_id', store=True)
    amount_paid = fields.Monetary(default=0.0, currency_field='currency_id', copy=False,
                                   help='Total already received via Customer Receipt - updated from there.')
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

    @api.onchange('so_ref_id')
    def _onchange_so_ref_id(self):
        if self.so_ref_id:
            self.partner_id = self.so_ref_id.partner_id
            self.line_ids = [(5, 0, 0)] + [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'qty': line.qty,
                'price_unit': line.price_unit,
            }) for line in self.so_ref_id.line_ids]

    @api.onchange('delivery_ref_id')
    def _onchange_delivery_ref_id(self):
        if self.delivery_ref_id:
            self.partner_id = self.delivery_ref_id.partner_id

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
                raise UserError(_('The Invoice cannot be empty.'))
            move_line_vals = [
                (0, 0, {
                    'account_id': self.env.ref('c18_basic_erp.acc_1_1200').id,
                    'debit': rec.amount_total,
                    'partner_id': rec.partner_id.id,
                    'cost_center_id': rec.cost_center_id.id,
                }),
                (0, 0, {
                    'account_id': rec.credit_account_id.id,
                    'credit': rec.amount_total,
                    'partner_id': rec.partner_id.id,
                    'cost_center_id': rec.cost_center_id.id,
                }),
            ]
            if not rec.delivery_ref_id:
                total_cogs = 0.0
                for line in rec.line_ids:
                    if line.product_id and line.product_id.product_type == 'barang_stok':
                        total_cogs += line.product_id._stock_consume(
                            line.qty, res_model=rec._name, res_id=rec.id, date=rec.date)
                if total_cogs:
                    move_line_vals += [
                        (0, 0, {
                            'account_id': self.env.ref('c18_basic_erp.acc_5_1000').id,
                            'debit': total_cogs,
                            'partner_id': rec.partner_id.id,
                            'cost_center_id': rec.cost_center_id.id,
                        }),
                        (0, 0, {
                            'account_id': self.env.ref('c18_basic_erp.acc_1_1300').id,
                            'credit': total_cogs,
                            'partner_id': rec.partner_id.id,
                            'cost_center_id': rec.cost_center_id.id,
                        }),
                    ]
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_pj').id,
                'date': rec.date,
                'ref': rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': move_line_vals,
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})

    def action_print_pdf(self):
        """Buka PDF di tab baru via /report/pdf (bukan route /report/download
        yang dipakai action manager utk ir.actions.report qweb-pdf) - route
        ini tidak set Content-Disposition, jadi browser tampilkan inline pakai
        native PDF viewer (rasio halaman A4 asli), bukan langsung men-download."""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'url': f'/report/pdf/c18_basic_erp.report_sale_invoice_document/{self.id}',
            'target': 'new',
        }


class SaleInvoiceLine(models.Model):
    _name = 'c18.sale.invoice.line'
    _description = 'Customer Invoice Line'
    _order = 'sequence, id'

    invoice_id = fields.Many2one('c18.sale.invoice', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('c18.product')
    name = fields.Char(string='Description')
    qty = fields.Float(default=1.0)
    price_unit = fields.Float(string='Unit Selling Price')
    subtotal = fields.Monetary(compute='_compute_subtotal', currency_field='currency_id', store=True)
    currency_id = fields.Many2one(related='invoice_id.currency_id')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and not self.name:
            self.name = self.product_id.name

    @api.depends('qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.price_unit
