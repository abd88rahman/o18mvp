from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockOpname(models.Model):
    _name = 'c18.account.stock.opname'
    _description = 'Stok Opname (Penyesuaian Persediaan)'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    product_id = fields.Many2one('c18.product', required=True, domain=[('product_type', '=', 'barang_stok')])
    qty_system = fields.Float(related='product_id.qty_on_hand', readonly=True,
                               help='Qty sistem saat ini - dibaca ulang saat posting utk hitung selisih final.')
    qty_physical = fields.Float(required=True, help='Hasil hitung fisik.')
    difference = fields.Float(compute='_compute_difference')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    note = fields.Char(string='Keterangan (alasan selisih)')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    amount = fields.Monetary(currency_field='currency_id', readonly=True, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.depends('qty_physical', 'qty_system')
    def _compute_difference(self):
        for rec in self:
            rec.difference = rec.qty_physical - rec.qty_system

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
            diff = rec.qty_physical - rec.product_id.qty_on_hand
            if not diff:
                raise UserError(_('Tidak ada selisih - tidak perlu posting.'))
            selisih_account = self.env.ref('c18_basic_erp.acc_6_1500')
            persediaan_account = self.env.ref('c18_basic_erp.acc_1_1300')
            if diff < 0:
                cost = rec.product_id._stock_consume(abs(diff))
                rec.amount = cost
                line_vals = [
                    (0, 0, {'account_id': selisih_account.id, 'debit': cost, 'cost_center_id': rec.cost_center_id.id}),
                    (0, 0, {'account_id': persediaan_account.id, 'credit': cost, 'cost_center_id': rec.cost_center_id.id}),
                ]
            else:
                unit_cost = rec.product_id._last_cost()
                rec.product_id._stock_receive(diff, unit_cost, rec._name, rec.id, date=rec.date)
                cost = diff * unit_cost
                rec.amount = cost
                line_vals = [
                    (0, 0, {'account_id': persediaan_account.id, 'debit': cost, 'cost_center_id': rec.cost_center_id.id}),
                    (0, 0, {'account_id': selisih_account.id, 'credit': cost, 'cost_center_id': rec.cost_center_id.id}),
                ]
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_sopn').id,
                'date': rec.date,
                'ref': rec.note or rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': line_vals,
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})
