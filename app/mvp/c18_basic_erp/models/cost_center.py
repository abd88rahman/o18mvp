from odoo import fields, models


class CostCenter(models.Model):
    _name = 'c18.account.cost.center'
    _description = 'Cost Center'
    _order = 'name'

    name = fields.Char(required=True, help='Bebas isi nama departemen atau nama project, sesuai kebutuhan.')
    code = fields.Char()
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
