from odoo import fields, models


class ExchangeRate(models.Model):
    _name = 'c18.account.exchange.rate'
    _description = 'Kurs Harian'
    _order = 'date desc'

    currency_id = fields.Many2one('res.currency', required=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    rate = fields.Float(required=True, digits=(12, 6), help='Nilai 1 unit currency_id dalam mata uang company.')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('currency_date_company_uniq', 'unique(currency_id, date, company_id)',
         'Hanya boleh ada 1 kurs per currency per tanggal per company.'),
    ]
