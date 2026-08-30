from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockOpname(models.Model):
    _name = 'c18.stock.opname'
    _description = 'Physical Inventory Count (Inventory Adjustment)'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True, string='Number')
    date = fields.Date(required=True, default=fields.Date.context_today)
    product_id = fields.Many2one('c18.product', required=True, domain=[('product_type', '=', 'barang_stok')])
    qty_system = fields.Float(related='product_id.qty_on_hand', readonly=True,
                               help='Current system qty - re-read at posting time to calculate the final difference.')
    qty_physical = fields.Float(required=True, help='Result of the physical count.')
    difference = fields.Float(compute='_compute_difference')
    unit_cost = fields.Float(string='Ending Unit Cost',
                              help='Periodic inventory system only - price used to value the physical count '
                                   '(Beginning Inventory + Purchases - Ending Inventory = COGS, see erd/mvp/06 F.3). '
                                   'Defaults to the last known cost, editable since it is a period-end estimate.')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    note = fields.Char(string='Notes (reason for discrepancy)')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    inventory_system = fields.Selection(related='company_id.inventory_system', readonly=True)
    amount = fields.Monetary(currency_field='currency_id', readonly=True, copy=False)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.depends('qty_physical', 'qty_system')
    def _compute_difference(self):
        for rec in self:
            rec.difference = rec.qty_physical - rec.qty_system

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id and not self.unit_cost:
            self.unit_cost = self.product_id._last_cost()

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
            if rec.company_id.inventory_system == 'periodic':
                rec._action_post_periodic()
            else:
                rec._action_post_perpetual()

    def _action_post_perpetual(self):
        self.ensure_one()
        rec = self
        diff = rec.qty_physical - rec.product_id.qty_on_hand
        if not diff:
            raise UserError(_('No discrepancy - nothing to post.'))
        selisih_account = self.env.ref('c18_basic_erp.acc_6_1500')
        persediaan_account = self.env.ref('c18_basic_erp.acc_1_1300')
        if diff < 0:
            cost = rec.product_id._stock_consume(
                abs(diff), res_model=rec._name, res_id=rec.id, date=rec.date)
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

    def _action_post_periodic(self):
        """Titik penutupan periodik (erd/mvp/06 poin F.3) - HPP = Persediaan Awal
        (periodic_book_value) + Pembelian (periodic_purchases_value) - Persediaan Akhir
        (qty_physical x unit_cost). Jurnal 3-baris: nolkan Pembelian, sesuaikan Persediaan
        dari nilai awal ke nilai akhir, HPP sbg angka penyeimbang."""
        self.ensure_one()
        rec = self
        product = rec.product_id
        beginning_value = product.periodic_book_value
        purchases_value = product.periodic_purchases_value
        unit_cost = rec.unit_cost or product._last_cost()
        ending_value = rec.qty_physical * unit_cost
        persediaan_delta = ending_value - beginning_value
        if not purchases_value and not persediaan_delta:
            raise UserError(_('No Purchases accumulated and no change in Inventory value - nothing to close.'))
        cogs = beginning_value + purchases_value - ending_value
        persediaan_account = self.env.ref('c18_basic_erp.acc_1_1300')
        pembelian_account = self.env.ref('c18_basic_erp.acc_5_1100')
        hpp_account = self.env.ref('c18_basic_erp.acc_5_1000')
        line_vals = []
        if purchases_value:
            line_vals.append((0, 0, {'account_id': pembelian_account.id, 'credit': purchases_value,
                                      'cost_center_id': rec.cost_center_id.id}))
        if persediaan_delta > 0:
            line_vals.append((0, 0, {'account_id': persediaan_account.id, 'debit': persediaan_delta,
                                      'cost_center_id': rec.cost_center_id.id}))
        elif persediaan_delta < 0:
            line_vals.append((0, 0, {'account_id': persediaan_account.id, 'credit': -persediaan_delta,
                                      'cost_center_id': rec.cost_center_id.id}))
        if cogs > 0:
            line_vals.append((0, 0, {'account_id': hpp_account.id, 'debit': cogs,
                                      'cost_center_id': rec.cost_center_id.id}))
        elif cogs < 0:
            line_vals.append((0, 0, {'account_id': hpp_account.id, 'credit': -cogs,
                                      'cost_center_id': rec.cost_center_id.id}))
        rec.amount = cogs
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
        product.write({
            'periodic_book_value': ending_value,
            'periodic_purchases_qty': 0.0,
            'periodic_purchases_value': 0.0,
            'qty_on_hand': rec.qty_physical,
        })
        rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})
