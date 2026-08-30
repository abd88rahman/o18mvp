from odoo import fields, models


class StockConsumption(models.Model):
    _name = 'c18.stock.consumption'
    _description = 'FIFO Stock Consumption Audit Log (per-layer breakdown per outbound transaction)'
    _order = 'date, id'

    # Ditambah 2026-08-30 supaya Kartu Stok (erd/mvp/06 poin F) bisa split
    # baris keluar per layer FIFO secara akurat - c18.stock.layer
    # cuma nyimpan state SAAT INI (qty_remaining), bukan histori per-transaksi,
    # jadi tanpa tabel ini breakdown per-layer tidak bisa direkonstruksi dari
    # data yang sudah lewat. 1 baris = 1 layer yang kena konsumsi oleh 1
    # transaksi keluar (kalau 1 transaksi kena 2 layer, jadi 2 baris di sini).
    product_id = fields.Many2one('c18.product', required=True, index=True)
    date = fields.Date(required=True)
    layer_id = fields.Many2one('c18.stock.layer', required=True, ondelete='restrict')
    qty = fields.Float(required=True)
    unit_cost = fields.Float(required=True)
    res_model = fields.Char()
    res_id = fields.Integer()
