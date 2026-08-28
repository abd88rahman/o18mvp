from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleReceipt(models.Model):
    _name = 'c18.sale.receipt'
    _description = 'Penerimaan Piutang'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    partner_id = fields.Many2one('res.partner', string='Customer', required=True)
    account_id = fields.Many2one('c18.account.account', string='Akun Debit', required=True,
                                  help='Default Kas/Bank, tapi boleh akun lain (Hutang Usaha utk netting, '
                                       'Persediaan utk barter, Uang Muka Penjualan utk apply DP).')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many('c18.sale.receipt.line', 'receipt_id', copy=True)
    deduction_ids = fields.One2many('c18.sale.receipt.deduction', 'receipt_id', copy=True,
                                     help='Simplifikasi (2026-08-27): deduction level header, bukan per-baris invoice seperti draft requirement asal.')
    amount_received_total = fields.Monetary(compute='_compute_totals', currency_field='currency_id', store=True)
    amount_deduction_total = fields.Monetary(compute='_compute_totals', currency_field='currency_id', store=True)
    amount_net = fields.Monetary(compute='_compute_totals', currency_field='currency_id', store=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.depends('line_ids.amount_received', 'deduction_ids.amount')
    def _compute_totals(self):
        for rec in self:
            rec.amount_received_total = sum(rec.line_ids.mapped('amount_received'))
            rec.amount_deduction_total = sum(rec.deduction_ids.mapped('amount'))
            rec.amount_net = rec.amount_received_total - rec.amount_deduction_total

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
                raise UserError(_('Penerimaan Piutang butuh minimal 1 baris invoice.'))
            for line in rec.line_ids:
                if line.amount_received > line.amount_residual + 0.001:
                    raise UserError(_('Nominal terima tidak boleh lebih dari sisa piutang (%s).', line.invoice_id.name))
            move_line_vals = []
            for line in rec.line_ids:
                move_line_vals.append((0, 0, {
                    'account_id': self.env.ref('c18_basic_erp.acc_1_1200').id,
                    'credit': line.amount_received,
                    'partner_id': rec.partner_id.id,
                    'cost_center_id': rec.cost_center_id.id,
                }))
            for ded in rec.deduction_ids:
                if ded.amount > 0:
                    move_line_vals.append((0, 0, {
                        'account_id': ded.account_id.id, 'debit': ded.amount,
                        'name': ded.name, 'cost_center_id': rec.cost_center_id.id,
                    }))
                elif ded.amount < 0:
                    move_line_vals.append((0, 0, {
                        'account_id': ded.account_id.id, 'credit': abs(ded.amount),
                        'name': ded.name, 'cost_center_id': rec.cost_center_id.id,
                    }))
            move_line_vals.append((0, 0, {
                'account_id': rec.account_id.id,
                'debit': rec.amount_net,
                'partner_id': rec.partner_id.id,
                'cost_center_id': rec.cost_center_id.id,
            }))
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_bpp').id,
                'date': rec.date,
                'ref': rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': move_line_vals,
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            for line in rec.line_ids:
                line.invoice_id.amount_paid += line.amount_received
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})


class SaleReceiptLine(models.Model):
    _name = 'c18.sale.receipt.line'
    _description = 'Penerimaan Piutang Line'
    _order = 'sequence, id'

    receipt_id = fields.Many2one('c18.sale.receipt', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    invoice_id = fields.Many2one('c18.sale.invoice', required=True,
                                  domain="[('partner_id', '=', parent.partner_id), ('state', '=', 'posted'), ('amount_residual', '>', 0)]")
    amount_original = fields.Monetary(related='invoice_id.amount_total', currency_field='currency_id', readonly=True)
    amount_residual = fields.Monetary(related='invoice_id.amount_residual', currency_field='currency_id', readonly=True)
    amount_received = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(related='receipt_id.currency_id')


class SaleReceiptDeduction(models.Model):
    _name = 'c18.sale.receipt.deduction'
    _description = 'Penerimaan Piutang - Deduction'
    _order = 'sequence, id'

    receipt_id = fields.Many2one('c18.sale.receipt', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Keterangan', required=True)
    account_id = fields.Many2one('c18.account.account', required=True)
    amount = fields.Monetary(currency_field='currency_id',
                              help='Positif = pengurang (debit akun ini, mis. Potongan Penjualan - kita rugi). '
                                   'Negatif = penambah (kredit akun ini, mis. Pendapatan Denda).')
    currency_id = fields.Many2one(related='receipt_id.currency_id')
