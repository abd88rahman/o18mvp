from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    costing_method = fields.Selection(
        [('fifo', 'FIFO'), ('average', 'Average')],
        default='average', required=True,
        help='Metode costing Persediaan, berlaku sama ke semua produk Barang Stok (bukan per produk).')
