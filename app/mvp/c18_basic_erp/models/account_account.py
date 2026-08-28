from odoo import fields, models

ACCOUNT_TYPES = [
    ('kas_bank', 'Kas Bank'),
    ('piutang_usaha', 'Piutang Usaha'),
    ('persediaan', 'Persediaan'),
    ('aktiva_lancar_lainnya', 'Aktiva Lancar Lainnya'),
    ('aktiva_tetap', 'Aktiva Tetap'),
    ('aktiva_lain', 'Aktiva Lain'),
    ('hutang_usaha', 'Hutang Usaha'),
    ('hutang_lancar_lainnya', 'Hutang Lancar Lainnya'),
    ('hutang_jangka_panjang', 'Hutang Jangka Panjang'),
    ('ekuitas', 'Ekuitas'),
    ('pendapatan', 'Pendapatan'),
    ('beban_pokok_pendapatan', 'Beban Pokok Pendapatan'),
    ('beban_usaha', 'Beban Usaha'),
    ('pendapatan_luar_usaha', 'Pendapatan di Luar Usaha'),
    ('beban_luar_usaha', 'Beban di Luar Usaha'),
]


class AccountAccount(models.Model):
    _name = 'c18.account.account'
    _description = 'Chart of Accounts'
    _order = 'code'

    code = fields.Char(required=True)
    name = fields.Char(required=True)
    account_type = fields.Selection(ACCOUNT_TYPES, required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)', 'Kode akun harus unik per company.'),
    ]

    def name_get(self):
        return [(rec.id, f'{rec.code} {rec.name}') for rec in self]
