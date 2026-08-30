from odoo import fields, models


class StockLayer(models.Model):
    _name = 'c18.stock.layer'
    _description = 'FIFO Stock Layer'
    _order = 'date, id'

    product_id = fields.Many2one('c18.product', required=True, index=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    qty_in = fields.Float(required=True)
    qty_remaining = fields.Float(required=True)
    unit_cost = fields.Float(required=True)
    res_model = fields.Char()
    res_id = fields.Integer()
