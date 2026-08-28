from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchasePayment(models.Model):
    _name = 'c18.purchase.payment'
    _description = 'Pembayaran Vendor'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    account_id = fields.Many2one('c18.account.account', string='Akun Kredit', required=True,
                                  help='Default Kas/Bank, tapi boleh akun lain (Piutang Usaha utk netting, '
                                       'Persediaan utk barter, Ekuitas utk debt-to-equity, Uang Muka Pembelian utk apply DP).')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many('c18.purchase.payment.line', 'payment_id', copy=True)
    deduction_ids = fields.One2many('c18.purchase.payment.deduction', 'payment_id', copy=True,
                                     help='Simplifikasi (2026-08-27): deduction level header, bukan per-baris invoice seperti draft requirement asal.')
    amount_paid_total = fields.Monetary(compute='_compute_totals', currency_field='currency_id', store=True)
    amount_deduction_total = fields.Monetary(compute='_compute_totals', currency_field='currency_id', store=True)
    amount_net = fields.Monetary(compute='_compute_totals', currency_field='currency_id', store=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.depends('line_ids.amount_paid', 'deduction_ids.amount')
    def _compute_totals(self):
        for rec in self:
            rec.amount_paid_total = sum(rec.line_ids.mapped('amount_paid'))
            rec.amount_deduction_total = sum(rec.deduction_ids.mapped('amount'))
            rec.amount_net = rec.amount_paid_total - rec.amount_deduction_total

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
                raise UserError(_('Pembayaran Vendor butuh minimal 1 baris invoice.'))
            for line in rec.line_ids:
                if line.amount_paid > line.amount_residual + 0.001:
                    raise UserError(_('Nominal bayar tidak boleh lebih dari sisa tagihan (%s).', line.bill_id.name))
            move_line_vals = []
            for line in rec.line_ids:
                move_line_vals.append((0, 0, {
                    'account_id': self.env.ref('c18_basic_erp.acc_2_1000').id,
                    'debit': line.amount_paid,
                    'partner_id': rec.partner_id.id,
                    'cost_center_id': rec.cost_center_id.id,
                }))
            for ded in rec.deduction_ids:
                if ded.amount > 0:
                    move_line_vals.append((0, 0, {
                        'account_id': ded.account_id.id, 'credit': ded.amount,
                        'name': ded.name, 'cost_center_id': rec.cost_center_id.id,
                    }))
                elif ded.amount < 0:
                    move_line_vals.append((0, 0, {
                        'account_id': ded.account_id.id, 'debit': abs(ded.amount),
                        'name': ded.name, 'cost_center_id': rec.cost_center_id.id,
                    }))
            move_line_vals.append((0, 0, {
                'account_id': rec.account_id.id,
                'credit': rec.amount_net,
                'partner_id': rec.partner_id.id,
                'cost_center_id': rec.cost_center_id.id,
            }))
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_bpv').id,
                'date': rec.date,
                'ref': rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': move_line_vals,
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            for line in rec.line_ids:
                line.bill_id.amount_paid += line.amount_paid
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})


class PurchasePaymentLine(models.Model):
    _name = 'c18.purchase.payment.line'
    _description = 'Pembayaran Vendor Line'
    _order = 'sequence, id'

    payment_id = fields.Many2one('c18.purchase.payment', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    bill_id = fields.Many2one('c18.purchase.bill', required=True,
                               domain="[('partner_id', '=', parent.partner_id), ('state', '=', 'posted'), ('amount_residual', '>', 0)]")
    amount_original = fields.Monetary(related='bill_id.amount_total', currency_field='currency_id', readonly=True)
    amount_residual = fields.Monetary(related='bill_id.amount_residual', currency_field='currency_id', readonly=True)
    amount_paid = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(related='payment_id.currency_id')


class PurchasePaymentDeduction(models.Model):
    _name = 'c18.purchase.payment.deduction'
    _description = 'Pembayaran Vendor - Deduction'
    _order = 'sequence, id'

    payment_id = fields.Many2one('c18.purchase.payment', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Keterangan', required=True)
    account_id = fields.Many2one('c18.account.account', required=True)
    amount = fields.Monetary(currency_field='currency_id',
                              help='Positif = pengurang (kredit akun ini, mis. Potongan Pembelian). '
                                   'Negatif = penambah (debit akun ini, mis. Beban Admin Bank).')
    currency_id = fields.Many2one(related='payment_id.currency_id')
