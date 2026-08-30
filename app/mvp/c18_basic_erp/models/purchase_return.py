from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseReturn(models.Model):
    _name = 'c18.purchase.return'
    _description = 'Vendor Return'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True, string='Number')
    date = fields.Date(required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    grni_ref_id = fields.Many2one('c18.purchase.receipt', string='Goods Receipt (before invoice)')
    bill_id = fields.Many2one('c18.purchase.bill', string='Vendor Bill (after invoice)')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many('c18.purchase.return.line', 'return_id', copy=True)
    amount_total = fields.Monetary(compute='_compute_amount_total', currency_field='currency_id', store=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.depends('line_ids.cost_amount')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('cost_amount'))

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
            if not rec.grni_ref_id and not rec.bill_id:
                raise UserError(_('The Return must reference a Goods Receipt (not yet invoiced) or a Vendor Bill (already invoiced).'))
            debit_account = self.env.ref('c18_basic_erp.acc_2_1000') if rec.bill_id else self.env.ref('c18_basic_erp.acc_2_1100')
            credit_account = (self.env.ref('c18_basic_erp.acc_5_1100')
                               if rec.company_id.inventory_system == 'periodic'
                               else self.env.ref('c18_basic_erp.acc_1_1300'))
            for line in rec.line_ids:
                if line.product_id.product_type == 'barang_stok':
                    line.cost_amount = line.product_id._stock_consume_latest(
                        line.qty, res_model=rec._name, res_id=rec.id, date=rec.date)
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_rtbv').id,
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
                        'account_id': credit_account.id,
                        'credit': rec.amount_total,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ],
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            if rec.bill_id:
                rec.bill_id.amount_paid += rec.amount_total
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})


class PurchaseReturnLine(models.Model):
    _name = 'c18.purchase.return.line'
    _description = 'Vendor Return Line'
    _order = 'sequence, id'

    return_id = fields.Many2one('c18.purchase.return', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    product_id = fields.Many2one('c18.product', required=True)
    qty = fields.Float(default=1.0)
    cost_amount = fields.Monetary(currency_field='currency_id', readonly=True,
                                   help='Value removed from Inventory, calculated at posting time by the costing engine.')
    currency_id = fields.Many2one(related='return_id.currency_id')
