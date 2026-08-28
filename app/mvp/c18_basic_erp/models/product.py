from odoo import _, fields, models
from odoo.exceptions import UserError

PRODUCT_TYPES = [
    ('barang_stok', 'Barang Stok'),
    ('jasa', 'Jasa'),
    ('barang_non_stok', 'Barang Non Stok'),
]


class Product(models.Model):
    _name = 'c18.product'
    _description = 'Product (tier Basic - tanpa kategori/UoM)'
    _order = 'code'

    code = fields.Char(required=True, help='Format bebas karakter, konvensi prefix menentukan kelompok (mirip pola CoA), tidak divalidasi sistem.')
    name = fields.Char(required=True)
    product_type = fields.Selection(PRODUCT_TYPES, required=True, default='barang_stok')
    is_purchaseable = fields.Boolean(default=True)
    is_saleable = fields.Boolean(default=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    qty_on_hand = fields.Float(default=0.0, readonly=True)
    avg_cost = fields.Float(default=0.0, readonly=True, help='Harga rata-rata berjalan (dipakai kalau company costing_method = Average).')

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)', 'Kode produk harus unik per company.'),
    ]

    def name_get(self):
        return [(rec.id, f'{rec.code} {rec.name}') for rec in self]

    def _stock_receive(self, qty, unit_cost, res_model, res_id, date=None):
        """Persediaan bertambah (Penerimaan Barang/Retur Customer) - erd/mvp/06 poin F."""
        self.ensure_one()
        if self.product_type != 'barang_stok' or qty <= 0:
            return
        if self.company_id.costing_method == 'fifo':
            self.env['c18.account.stock.layer'].create({
                'product_id': self.id,
                'date': date or fields.Date.context_today(self),
                'qty_in': qty,
                'qty_remaining': qty,
                'unit_cost': unit_cost,
                'res_model': res_model,
                'res_id': res_id,
            })
            new_qty = self.qty_on_hand + qty
            self.qty_on_hand = new_qty
        else:
            old_value = self.qty_on_hand * self.avg_cost
            new_qty = self.qty_on_hand + qty
            new_avg = (old_value + qty * unit_cost) / new_qty if new_qty else 0.0
            self.write({'qty_on_hand': new_qty, 'avg_cost': new_avg})

    def _stock_consume(self, qty):
        """Persediaan berkurang (Pengiriman/Penjualan langsung/Retur Vendor/Pemakaian Sendiri).
        Return nilai HPP/beban total dari qty yang dikonsumsi. Stok negatif tidak diperbolehkan."""
        self.ensure_one()
        if self.product_type != 'barang_stok' or qty <= 0:
            return 0.0
        if qty > self.qty_on_hand + 1e-6:
            raise UserError(_('Stok %(product)s tidak cukup (tersedia %(available)s, diminta %(requested)s).',
                               product=self.name, available=self.qty_on_hand, requested=qty))
        if self.company_id.costing_method == 'fifo':
            layers = self.env['c18.account.stock.layer'].search(
                [('product_id', '=', self.id), ('qty_remaining', '>', 0)], order='date, id')
            remaining_to_consume = qty
            total_cost = 0.0
            for layer in layers:
                if remaining_to_consume <= 0:
                    break
                consumed = min(layer.qty_remaining, remaining_to_consume)
                total_cost += consumed * layer.unit_cost
                layer.qty_remaining -= consumed
                remaining_to_consume -= consumed
            self.qty_on_hand -= qty
            return total_cost
        else:
            total_cost = qty * self.avg_cost
            self.qty_on_hand -= qty
            return total_cost

    def _stock_consume_latest(self, qty):
        """Retur Barang Vendor (erd/mvp/06 poin F.3) - default konsumsi dari layer TERBARU
        (asumsi retur biasanya cepat setelah terima), beda dari _stock_consume yang dari layer
        terlama. Average: sama seperti _stock_consume (avg_cost tidak dipengaruhi arah)."""
        self.ensure_one()
        if self.product_type != 'barang_stok' or qty <= 0:
            return 0.0
        if qty > self.qty_on_hand + 1e-6:
            raise UserError(_('Stok %(product)s tidak cukup (tersedia %(available)s, diminta %(requested)s).',
                               product=self.name, available=self.qty_on_hand, requested=qty))
        if self.company_id.costing_method == 'fifo':
            layers = self.env['c18.account.stock.layer'].search(
                [('product_id', '=', self.id), ('qty_remaining', '>', 0)], order='date desc, id desc')
            remaining_to_consume = qty
            total_cost = 0.0
            for layer in layers:
                if remaining_to_consume <= 0:
                    break
                consumed = min(layer.qty_remaining, remaining_to_consume)
                total_cost += consumed * layer.unit_cost
                layer.qty_remaining -= consumed
                remaining_to_consume -= consumed
            self.qty_on_hand -= qty
            return total_cost
        else:
            total_cost = qty * self.avg_cost
            self.qty_on_hand -= qty
            return total_cost

    def _last_cost(self):
        """Estimasi harga HPP terakhir - dipakai Retur Barang Customer (E.5) kalau tidak ada
        referensi delivery yang jelas, dan Stok Opname (F.2) selisih positif. Approximation
        (bukan trace exact per-dokumen)."""
        self.ensure_one()
        if self.company_id.costing_method == 'fifo':
            last_layer = self.env['c18.account.stock.layer'].search(
                [('product_id', '=', self.id)], order='date desc, id desc', limit=1)
            return last_layer.unit_cost if last_layer else 0.0
        return self.avg_cost
