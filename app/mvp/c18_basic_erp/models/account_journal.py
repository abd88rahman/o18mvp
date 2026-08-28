from odoo import fields, models


class AccountJournal(models.Model):
    _name = 'c18.account.journal'
    _description = 'Journal Type'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char(required=True, help='Kode prefix nomor dokumen, mis. JU, KM, PNBR (maks 4 huruf).')
    sequence = fields.Integer(default=10)
    sequence_id = fields.Many2one('ir.sequence', required=True, help='Sequence penomoran definitif dokumen jenis ini.')
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)', 'Kode jurnal harus unik per company.'),
    ]
