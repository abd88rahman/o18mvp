from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseWriteoff(models.Model):
    _name = 'c18.purchase.writeoff'
    _description = 'Accounts Payable Write-off'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True, string='Number')
    date = fields.Date(required=True, default=fields.Date.context_today)
    bill_id = fields.Many2one('c18.purchase.bill', required=True, string='Vendor Bill',
                               domain=[('state', '=', 'posted'), ('amount_residual', '>', 0)])
    partner_id = fields.Many2one('res.partner', related='bill_id.partner_id', store=True, readonly=True)
    amount = fields.Monetary(currency_field='currency_id', required=True,
                              help='Defaults to the outstanding balance, editable but cannot exceed it.')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    note = fields.Char(string='Notes')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.onchange('bill_id')
    def _onchange_bill_id(self):
        if self.bill_id:
            self.amount = self.bill_id.amount_residual

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
            if rec.amount > rec.bill_id.amount_residual + 0.001:
                raise UserError(_('The write-off amount cannot exceed the outstanding payable balance (%s).', rec.bill_id.name))
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_woht').id,
                'date': rec.date,
                'ref': rec.note or rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_2_1000').id,
                        'debit': rec.amount,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_8_1000').id,
                        'credit': rec.amount,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ],
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.bill_id.amount_paid += rec.amount
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})
