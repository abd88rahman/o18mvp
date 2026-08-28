from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_customer = fields.Boolean(string='Customer')
    is_vendor = fields.Boolean(string='Vendor')
    npwp = fields.Char(string='NPWP')
    payment_term_days = fields.Integer(string='Termin Pembayaran (hari)', default=0)
