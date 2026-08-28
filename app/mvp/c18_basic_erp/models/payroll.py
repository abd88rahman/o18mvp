from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PayrollAccrual(models.Model):
    _name = 'c18.payroll.accrual'
    _description = 'Payroll - Jurnal Pengakuan (Hutang Gaji)'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', help='Opsional - karyawan/pihak terkait.')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    amount = fields.Monetary(currency_field='currency_id', required=True)
    amount_paid = fields.Monetary(default=0.0, currency_field='currency_id', copy=False)
    amount_residual = fields.Monetary(compute='_compute_amount_residual', currency_field='currency_id', store=True)
    note = fields.Char(string='Keterangan')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.depends('amount', 'amount_paid')
    def _compute_amount_residual(self):
        for rec in self:
            rec.amount_residual = rec.amount - rec.amount_paid

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
                raise UserError(_('Jumlah wajib diisi.'))
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_hgj').id,
                'date': rec.date,
                'ref': rec.note or rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_6_1000').id,
                        'debit': rec.amount,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_2_1300').id,
                        'credit': rec.amount,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ],
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})

    def action_pay(self):
        self.ensure_one()
        payment = self.env['c18.payroll.payment'].create({
            'partner_id': self.partner_id.id,
            'line_ids': [(0, 0, {
                'accrual_id': self.id,
                'amount_paid': self.amount_residual,
            })],
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'c18.payroll.payment',
            'view_mode': 'form',
            'res_id': payment.id,
        }


class PayrollPayment(models.Model):
    _name = 'c18.payroll.payment'
    _description = 'Payroll - Jurnal Pembayaran (Bayar Gaji)'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner')
    account_id = fields.Many2one('c18.account.account', string='Akun Kas/Bank', required=True,
                                  domain=[('account_type', '=', 'kas_bank')])
    cost_center_id = fields.Many2one('c18.account.cost.center')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many('c18.payroll.payment.line', 'payment_id', copy=True)
    amount_total = fields.Monetary(compute='_compute_amount_total', currency_field='currency_id', store=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.depends('line_ids.amount_paid')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('amount_paid'))

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
                raise UserError(_('Jurnal Pembayaran butuh minimal 1 baris Jurnal Pengakuan.'))
            for line in rec.line_ids:
                if line.amount_paid > line.amount_residual + 0.001:
                    raise UserError(_('Nominal bayar tidak boleh lebih dari sisa hutang gaji (%s).', line.accrual_id.name))
            move_line_vals = []
            for line in rec.line_ids:
                move_line_vals.append((0, 0, {
                    'account_id': self.env.ref('c18_basic_erp.acc_2_1300').id,
                    'debit': line.amount_paid,
                    'partner_id': rec.partner_id.id,
                    'cost_center_id': rec.cost_center_id.id,
                }))
            move_line_vals.append((0, 0, {
                'account_id': rec.account_id.id,
                'credit': rec.amount_total,
                'partner_id': rec.partner_id.id,
                'cost_center_id': rec.cost_center_id.id,
            }))
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_bgj').id,
                'date': rec.date,
                'ref': rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': move_line_vals,
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            for line in rec.line_ids:
                line.accrual_id.amount_paid += line.amount_paid
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})


class PayrollPaymentLine(models.Model):
    _name = 'c18.payroll.payment.line'
    _description = 'Jurnal Pembayaran Line'
    _order = 'sequence, id'

    payment_id = fields.Many2one('c18.payroll.payment', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    accrual_id = fields.Many2one('c18.payroll.accrual', required=True, string='Jurnal Pengakuan',
                                  domain=[('state', '=', 'posted'), ('amount_residual', '>', 0)])
    amount_original = fields.Monetary(related='accrual_id.amount', currency_field='currency_id', readonly=True)
    amount_residual = fields.Monetary(related='accrual_id.amount_residual', currency_field='currency_id', readonly=True)
    amount_paid = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(related='payment_id.currency_id')
