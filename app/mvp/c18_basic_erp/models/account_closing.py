from odoo import _, api, fields, models
from odoo.exceptions import UserError

PL_ACCOUNT_TYPES = [
    'revenue',
    'cost_of_revenue',
    'expense',
    'other_revenue',
    'other_expense',
]


class AccountClosing(models.Model):
    _name = 'c18.account.closing'
    _description = 'Period Closing (Closing Entries)'
    _order = 'closing_date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True, string='Number')
    fiscal_year = fields.Integer(required=True, default=lambda self: fields.Date.context_today(self).year - 1)
    closing_date = fields.Date(compute='_compute_closing_date', store=True, readonly=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.depends('fiscal_year')
    def _compute_closing_date(self):
        for rec in self:
            rec.closing_date = fields.Date.to_date(f'{rec.fiscal_year}-12-31') if rec.fiscal_year else False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.name == 'New':
                rec.name = f'draft-{rec.id}'
        return records

    def action_process(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            existing = self.env['c18.account.closing'].search([
                ('company_id', '=', rec.company_id.id),
                ('state', '=', 'posted'),
                ('fiscal_year', '=', rec.fiscal_year),
                ('id', '!=', rec.id),
            ])
            if existing:
                raise UserError(_('Fiscal year %s has already been closed.', rec.fiscal_year))

            date_from = fields.Date.to_date(f'{rec.fiscal_year}-01-01')
            date_to = rec.closing_date
            pl_accounts = self.env['c18.account.account'].search([
                ('company_id', '=', rec.company_id.id),
                ('account_type', 'in', PL_ACCOUNT_TYPES),
            ])
            move_line_vals = []
            debit_total = 0.0
            credit_total = 0.0
            for account in pl_accounts:
                lines = self.env['c18.account.move.line'].search([
                    ('account_id', '=', account.id),
                    ('state', '=', 'posted'),
                    ('date', '>=', date_from),
                    ('date', '<=', date_to),
                    ('move_id.is_closing_entry', '=', False),
                ])
                # Konversi ke company currency dulu (erd/mvp/01 poin 5) - jangan
                # jumlah debit/credit mentah, bisa campur currency lintas jurnal.
                net = sum(lines.mapped('debit_company_currency')) - sum(lines.mapped('credit_company_currency'))
                if not net:
                    continue
                if net > 0:
                    move_line_vals.append((0, 0, {'account_id': account.id, 'credit': net}))
                    credit_total += net
                else:
                    move_line_vals.append((0, 0, {'account_id': account.id, 'debit': abs(net)}))
                    debit_total += abs(net)

            if not move_line_vals:
                raise UserError(_('No Revenue/Expense balances for year %s to close.', rec.fiscal_year))

            diff = debit_total - credit_total
            laba_ditahan = self.env.ref('c18_basic_erp.acc_3_1100')
            if diff > 0:
                move_line_vals.append((0, 0, {'account_id': laba_ditahan.id, 'credit': diff}))
            elif diff < 0:
                move_line_vals.append((0, 0, {'account_id': laba_ditahan.id, 'debit': abs(diff)}))

            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_tutb').id,
                'date': rec.closing_date,
                'ref': _('Period Closing %s', rec.fiscal_year),
                'company_id': rec.company_id.id,
                'is_closing_entry': True,
                'line_ids': move_line_vals,
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})
