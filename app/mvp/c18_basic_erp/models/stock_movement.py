from odoo import fields, models


class StockMovement(models.Model):
    _name = 'c18.stock.movement'
    _description = 'Stock Movement Audit Log (Average costing method only)'
    _order = 'date, id'

    # Ditambah 2026-08-30. Beda dari c18.stock.layer/.stock.consumption
    # (khusus mesin costing FIFO) - tabel ini murni audit trail utk costing
    # Average, yang aslinya cuma mutasi 2 field running (qty_on_hand/avg_cost)
    # di c18.product tanpa nyimpan histori per-transaksi sama sekali. Tanpa
    # tabel ini, Kartu Stok (erd/mvp/06 poin F) tidak bisa dibangun untuk
    # produk ber-costing Average - default company malah Average, bukan FIFO.
    product_id = fields.Many2one('c18.product', required=True, index=True)
    date = fields.Date(required=True)
    qty = fields.Float(required=True, help='Positive = stock in, negative = stock out.')
    unit_cost = fields.Float(required=True,
                              help='Unit cost received (IN) or running avg_cost at that time (OUT).')
    res_model = fields.Char()
    res_id = fields.Integer()
