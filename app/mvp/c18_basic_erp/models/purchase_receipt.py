from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseReceipt(models.Model):
    _name = 'c18.purchase.receipt'
    _description = 'Goods Receipt'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True, string='Number')
    date = fields.Date(required=True, default=fields.Date.context_today)
    po_ref_id = fields.Many2one('c18.purchase.order', string='PO', domain=[('state', '=', 'confirmed')])
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    cost_center_id = fields.Many2one('c18.account.cost.center')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    line_ids = fields.One2many('c18.purchase.receipt.line', 'receipt_id', copy=True)
    amount_total = fields.Monetary(compute='_compute_amount_total', currency_field='currency_id', store=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)
    bill_id = fields.Many2one('c18.purchase.bill', readonly=True, copy=False)

    @api.depends('line_ids.subtotal')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = sum(rec.line_ids.mapped('subtotal'))

    @api.onchange('po_ref_id')
    def _onchange_po_ref_id(self):
        if self.po_ref_id:
            self.partner_id = self.po_ref_id.partner_id
            self.line_ids = [(5, 0, 0)] + [(0, 0, {
                'po_line_id': line.id,
                'product_id': line.product_id.id,
                'qty_received': line.qty,
                'price_unit': line.price_unit,
            }) for line in self.po_ref_id.line_ids]

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
                raise UserError(_('The Goods Receipt cannot be empty.'))
            for line in rec.line_ids:
                if line.product_id.product_type == 'barang_stok':
                    line.product_id._stock_receive(line.qty_received, line.price_unit,
                                                     rec._name, rec.id, date=rec.date)
            debit_account = (self.env.ref('c18_basic_erp.acc_5_1100')
                              if rec.company_id.inventory_system == 'periodic'
                              else self.env.ref('c18_basic_erp.acc_1_1300'))
            move = self.env['c18.account.move'].create({
                'journal_id': self.env.ref('c18_basic_erp.journal_pnbr').id,
                'date': rec.date,
                'ref': rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': debit_account.id,
                        'debit': rec.amount_total,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_2_1100').id,
                        'credit': rec.amount_total,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ],
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})

    def action_reset_to_draft(self):
        raise UserError(_('A posted Goods Receipt cannot be reset to draft (it affects Inventory) - create a separate correction document instead.'))

    def action_create_bill(self):
        self.ensure_one()
        bill = self.env['c18.purchase.bill'].create({
            'partner_id': self.partner_id.id,
            'po_ref_id': self.po_ref_id.id,
            'grni_ref_id': self.id,
            'cost_center_id': self.cost_center_id.id,
            'line_ids': [(0, 0, {
                'product_id': line.product_id.id,
                'name': line.product_id.name,
                'qty': line.qty_received,
                'price_unit': line.price_unit,
            }) for line in self.line_ids],
        })
        self.bill_id = bill.id
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'c18.purchase.bill',
            'view_mode': 'form',
            'res_id': bill.id,
        }


class PurchaseReceiptLine(models.Model):
    _name = 'c18.purchase.receipt.line'
    _description = 'Goods Receipt Line'
    _order = 'sequence, id'

    receipt_id = fields.Many2one('c18.purchase.receipt', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    po_line_id = fields.Many2one('c18.purchase.order.line')
    product_id = fields.Many2one('c18.product', required=True)
    qty_received = fields.Float(default=1.0)
    price_unit = fields.Float(string='Unit Price')
    subtotal = fields.Monetary(compute='_compute_subtotal', currency_field='currency_id', store=True)
    currency_id = fields.Many2one(related='receipt_id.currency_id')

    @api.depends('qty_received', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty_received * line.price_unit
