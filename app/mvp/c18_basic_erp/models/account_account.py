from odoo import fields, models

ACCOUNT_TYPES = [
    ('cash_bank', 'Cash/Bank'),
    ('receivable', 'Accounts Receivable'),
    ('inventory', 'Inventory'),
    ('other_current_asset', 'Other Current Assets'),
    ('fixed_asset', 'Fixed Assets'),
    ('other_asset', 'Other Assets'),
    ('payable', 'Accounts Payable'),
    ('other_current_liability', 'Other Current Liabilities'),
    ('long_term_liability', 'Long-term Liabilities'),
    ('equity', 'Equity'),
    ('revenue', 'Revenue'),
    ('cost_of_revenue', 'Cost of Revenue'),
    ('expense', 'Operating Expenses'),
    ('other_revenue', 'Other Income'),
    ('other_expense', 'Other Expenses'),
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
        ('code_company_uniq', 'unique(code, company_id)', 'Account code must be unique per company.'),
    ]

    def name_get(self):
        return [(rec.id, f'{rec.code} {rec.name}') for rec in self]
