from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountCash(models.Model):
    _name = 'c18.account.cash'
    _description = 'Cash/Bank (Cash In/Cash Out/Transfer)'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True, string='Number')
    date = fields.Date(required=True, default=fields.Date.context_today)
    journal_id = fields.Many2one('c18.account.journal', required=True, domain=[('code', 'in', ['KM', 'KK', 'TRF'])])
    is_transfer = fields.Boolean(compute='_compute_is_transfer', store=True)
    account_id = fields.Many2one('c18.account.account', required=True, string='Cash/Bank Account',
                                  domain=[('account_type', '=', 'cash_bank')])
    account_id_dest = fields.Many2one('c18.account.account', string='Destination Account',
                                       domain=[('account_type', '=', 'cash_bank')])
    partner_id = fields.Many2one('res.partner', help='Optional - can be an employee or other party without a formal receivable/payable.')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    amount = fields.Monetary(currency_field='currency_id', help='Transfer amount (Transfer type only).')
    note = fields.Char(string='Notes')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    line_ids = fields.One2many('c18.account.cash.line', 'cash_id', string='Contra Account')
    amount_total = fields.Monetary(compute='_compute_amount_total', currency_field='currency_id')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.depends('journal_id.code')
    def _compute_is_transfer(self):
        for rec in self:
            rec.is_transfer = rec.journal_id.code == 'TRF'

    @api.depends('line_ids.amount', 'amount', 'is_transfer')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.amount if rec.is_transfer else sum(rec.line_ids.mapped('amount'))

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
            move_line_vals = []
            if rec.is_transfer:
                if not rec.account_id_dest or not rec.amount:
                    raise UserError(_('A Transfer requires a Destination Account and an Amount.'))
                if rec.account_id_dest == rec.account_id:
                    raise UserError(_('The Destination Account cannot be the same as the source Cash/Bank Account.'))
                move_line_vals.append((0, 0, {
                    'account_id': rec.account_id_dest.id,
                    'debit': rec.amount,
                    'cost_center_id': rec.cost_center_id.id,
                    'name': rec.note,
                }))
                move_line_vals.append((0, 0, {
                    'account_id': rec.account_id.id,
                    'credit': rec.amount,
                    'cost_center_id': rec.cost_center_id.id,
                    'name': rec.note,
                }))
            else:
                if not rec.line_ids:
                    raise UserError(_('Cash In/Cash Out requires at least 1 contra account line.'))
                if any(line.account_id.account_type == 'cash_bank' for line in rec.line_ids):
                    raise UserError(_('The Contra Account cannot be a Cash/Bank account - use the Cash/Bank Transfer type for cash-to-cash movements.'))
                total = sum(rec.line_ids.mapped('amount'))
                header_side = 'debit' if rec.journal_id.code == 'KM' else 'credit'
                line_side = 'credit' if rec.journal_id.code == 'KM' else 'debit'
                move_line_vals.append((0, 0, {
                    'account_id': rec.account_id.id,
                    header_side: total,
                    'partner_id': rec.partner_id.id,
                    'cost_center_id': rec.cost_center_id.id,
                }))
                for line in rec.line_ids:
                    move_line_vals.append((0, 0, {
                        'account_id': line.account_id.id,
                        line_side: line.amount,
                        'name': line.name,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }))
            move = self.env['c18.account.move'].create({
                'journal_id': rec.journal_id.id,
                'date': rec.date,
                'ref': rec.note or rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': move_line_vals,
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})

    def action_reset_to_draft(self):
        for rec in self:
            if rec.move_id:
                rec.move_id.action_reset_to_draft()
            rec.write({'state': 'draft'})


class AccountCashLine(models.Model):
    _name = 'c18.account.cash.line'
    _description = 'Cash/Bank Line (contra account for Cash In/Cash Out)'
    _order = 'sequence, id'

    cash_id = fields.Many2one('c18.account.cash', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    account_id = fields.Many2one('c18.account.account', required=True, string='Contra Account')
    name = fields.Char(string='Description')
    amount = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(related='cash_id.currency_id')
