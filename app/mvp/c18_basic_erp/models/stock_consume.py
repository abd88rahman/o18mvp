from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockConsume(models.Model):
    _name = 'c18.account.stock.consume'
    _description = 'Pemakaian Sendiri (Consume)'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    product_id = fields.Many2one('c18.product', required=True, domain=[('product_type', '=', 'barang_stok')])
    qty = fields.Float(default=1.0, required=True)
    debit_account_id = fields.Many2one('c18.account.account', string='Akun Beban', required=True)
    cost_center_id = fields.Many2one('c18.account.cost.center')
    note = fields.Char(string='Keterangan (tujuan pemakaian)')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(currency_field='currency_id', readonly=True, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

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
            if not rec.qty:
                raise UserError(_('Qty wajib diisi.'))
            rec.amount = rec.product_id._stock_consume(rec.qty)
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_pmks').id,
                'date': rec.date,
                'ref': rec.note or rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': rec.debit_account_id.id,
                        'debit': rec.amount,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_1_1300').id,
                        'credit': rec.amount,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ],
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})
