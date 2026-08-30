from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleAdvance(models.Model):
    _name = 'c18.sale.advance'
    _description = 'Sales Advance'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True, string='Number')
    date = fields.Date(required=True, default=fields.Date.context_today)
    so_ref_id = fields.Many2one('c18.sale.order', string='SO', required=True, domain=[('state', '=', 'confirmed')])
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    account_id = fields.Many2one('c18.account.account', string='Cash/Bank Account', required=True,
                                  domain=[('account_type', '=', 'cash_bank')])
    cost_center_id = fields.Many2one('c18.account.cost.center')
    amount = fields.Monetary(currency_field='currency_id', required=True)
    note = fields.Char(string='Notes')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.onchange('so_ref_id')
    def _onchange_so_ref_id(self):
        if self.so_ref_id:
            self.partner_id = self.so_ref_id.partner_id

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
            if not rec.amount:
                raise UserError(_('Amount is required.'))
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_umpj').id,
                'date': rec.date,
                'ref': rec.note or rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': rec.account_id.id,
                        'debit': rec.amount,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_2_1200').id,
                        'credit': rec.amount,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ],
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})
