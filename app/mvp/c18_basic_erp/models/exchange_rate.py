from odoo import fields, models


class ExchangeRate(models.Model):
    _name = 'c18.account.exchange.rate'
    _description = 'Daily Exchange Rate'
    _order = 'date desc'

    currency_id = fields.Many2one('res.currency', required=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    rate = fields.Float(required=True, digits=(12, 6), help='Value of 1 unit of currency_id in the company currency.')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('currency_date_company_uniq', 'unique(currency_id, date, company_id)',
         'Only 1 exchange rate is allowed per currency per date per company.'),
    ]
