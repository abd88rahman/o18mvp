from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleWriteoff(models.Model):
    _name = 'c18.sale.writeoff'
    _description = 'Write-off Piutang'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    invoice_id = fields.Many2one('c18.sale.invoice', required=True, string='Penjualan',
                                  domain=[('state', '=', 'posted'), ('amount_residual', '>', 0)])
    partner_id = fields.Many2one('res.partner', related='invoice_id.partner_id', store=True, readonly=True)
    amount = fields.Monetary(currency_field='currency_id', required=True,
                              help='Default sisa piutang, boleh diedit tapi tidak boleh lebih dari sisa.')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    note = fields.Char(string='Keterangan')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.onchange('invoice_id')
    def _onchange_invoice_id(self):
        if self.invoice_id:
            self.amount = self.invoice_id.amount_residual

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
            if rec.amount > rec.invoice_id.amount_residual + 0.001:
                raise UserError(_('Jumlah write-off tidak boleh lebih dari sisa piutang (%s).', rec.invoice_id.name))
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_wopt').id,
                'date': rec.date,
                'ref': rec.note or rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_6_1300').id,
                        'debit': rec.amount,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_1_1200').id,
                        'credit': rec.amount,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ],
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.invoice_id.amount_paid += rec.amount
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})
