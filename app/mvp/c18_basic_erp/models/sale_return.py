from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleReturn(models.Model):
    _name = 'c18.sale.return'
    _description = 'Customer Return'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True, string='Number')
    date = fields.Date(required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    delivery_ref_id = fields.Many2one('c18.sale.delivery', string='Delivery (not yet invoiced)')
    invoice_id = fields.Many2one('c18.sale.invoice', string='Customer Invoice (already invoiced)')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many('c18.sale.return.line', 'return_id', copy=True)
    amount_revenue_total = fields.Monetary(compute='_compute_amount_total', currency_field='currency_id', store=True,
                                            help='Reversal value for Accounts Receivable/Sales Returns & Allowances (only relevant when invoice_id is set).')
    amount_cost_total = fields.Monetary(compute='_compute_amount_total', currency_field='currency_id', store=True,
                                         help='Reversal value for Inventory/COGS - calculated by the costing engine at posting time.')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.depends('line_ids.price_unit', 'line_ids.qty', 'line_ids.cost_amount')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_revenue_total = sum(line.qty * line.price_unit for line in rec.line_ids)
            rec.amount_cost_total = sum(rec.line_ids.mapped('cost_amount'))

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        if self.invoice_id:
            self.partner_id = self.invoice_id.partner_id

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
                raise UserError(_('The Return cannot be empty.'))
            if not rec.delivery_ref_id and not rec.invoice_id:
                raise UserError(_('The Return must reference a Delivery (not yet invoiced) or a Customer Invoice (already invoiced).'))
            periodic = rec.company_id.inventory_system == 'periodic'
            move_line_vals = []
            for line in rec.line_ids:
                if line.product_id.product_type == 'barang_stok':
                    unit_cost = line.unit_cost_hint or line.product_id._last_cost()
                    line.product_id._stock_receive(line.qty, unit_cost, rec._name, rec.id, date=rec.date,
                                                     add_to_purchases_pool=False)
                    # Mode Periodik (erd/mvp/06 poin F.3): sisi keluar (Pengiriman/Penjualan) tidak
                    # pernah posting nilai, jadi sisi retur-nya juga tanpa nilai (simetris, tanpa jurnal HPP).
                    line.cost_amount = 0.0 if periodic else line.qty * unit_cost

            if not rec.invoice_id:
                if not rec.amount_cost_total:
                    # Mode Periodik (erd/mvp/06 poin F.3) - belum invoice & tanpa nilai HPP utk
                    # direverse, jadi tidak ada jurnal sama sekali (murni qty berkurang balik).
                    rec.write({'state': 'posted'})
                    continue
                # Baru sampai Pengiriman Barang, belum invoice - reverse cuma leg HPP/Persediaan.
                move_line_vals += [
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_1_1300').id,
                        'debit': rec.amount_cost_total,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_5_1000').id,
                        'credit': rec.amount_cost_total,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ]
            else:
                # Sudah invoice - reverse leg revenue (kontra-revenue), plus leg Persediaan/HPP kalau ada.
                move_line_vals += [
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_4_1100').id,
                        'debit': rec.amount_revenue_total,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_1_1200').id,
                        'credit': rec.amount_revenue_total,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ]
                if rec.amount_cost_total:
                    move_line_vals += [
                        (0, 0, {
                            'account_id': self.env.ref('c18_basic_erp.acc_1_1300').id,
                            'debit': rec.amount_cost_total,
                            'partner_id': rec.partner_id.id,
                            'cost_center_id': rec.cost_center_id.id,
                        }),
                        (0, 0, {
                            'account_id': self.env.ref('c18_basic_erp.acc_5_1000').id,
                            'credit': rec.amount_cost_total,
                            'partner_id': rec.partner_id.id,
                            'cost_center_id': rec.cost_center_id.id,
                        }),
                    ]
                rec.invoice_id.amount_paid += rec.amount_revenue_total

            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_rtbc').id,
                'date': rec.date,
                'ref': rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': move_line_vals,
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})


class SaleReturnLine(models.Model):
    _name = 'c18.sale.return.line'
    _description = 'Customer Return Line'
    _order = 'sequence, id'

    return_id = fields.Many2one('c18.sale.return', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('c18.product', required=True)
    qty = fields.Float(default=1.0)
    price_unit = fields.Float(string='Unit Selling Price',
                               help='From the original invoice - basis for the Accounts Receivable/Sales Returns & Allowances reversal.')
    unit_cost_hint = fields.Float(string='Estimated COGS/Unit',
                                   help='Optional - overrides the original COGS estimate (defaults to the last cost if left empty).')
    cost_amount = fields.Monetary(currency_field='currency_id', readonly=True)
    currency_id = fields.Many2one(related='return_id.currency_id')
