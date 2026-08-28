from odoo import _, api, fields, models
from odoo.exceptions import UserError


class PurchaseAdvance(models.Model):
    _name = 'c18.purchase.advance'
    _description = 'Uang Muka Pembelian'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    po_ref_id = fields.Many2one('c18.purchase.order', string='PO', required=True, domain=[('state', '=', 'confirmed')])
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    account_id = fields.Many2one('c18.account.account', string='Akun Kas/Bank', required=True,
                                  domain=[('account_type', '=', 'kas_bank')])
    cost_center_id = fields.Many2one('c18.account.cost.center')
    amount = fields.Monetary(currency_field='currency_id', required=True)
    note = fields.Char(string='Keterangan')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.onchange('po_ref_id')
    def _onchange_po_ref_id(self):
        if self.po_ref_id:
            self.partner_id = self.po_ref_id.partner_id

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
                'journal_id': self.env.ref('c18_basic_erp.journal_umpb').id,
                'date': rec.date,
                'ref': rec.note or rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'line_ids': [
                    (0, 0, {
                        'account_id': self.env.ref('c18_basic_erp.acc_1_1400').id,
                        'debit': rec.amount,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                    (0, 0, {
                        'account_id': rec.account_id.id,
                        'credit': rec.amount,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ],
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})
