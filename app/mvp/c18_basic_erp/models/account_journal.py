from odoo import fields, models


class AccountJournal(models.Model):
    _name = 'c18.account.journal'
    _description = 'Journal Type'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True, help='Document number prefix code, e.g. JU, KM, PNBR (max 4 letters).')
    sequence = fields.Integer(default=10)
    sequence_id = fields.Many2one('ir.sequence', required=True, help='The definitive numbering sequence for this document type.')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)', 'Journal code must be unique per company.'),
    ]
