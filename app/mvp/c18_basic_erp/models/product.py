from odoo import _, fields, models
from odoo.exceptions import UserError

PRODUCT_TYPES = [
    ('barang_stok', 'Stockable Product'),
    ('jasa', 'Service'),
    ('barang_non_stok', 'Non-Stock Product'),
]


class Product(models.Model):
    _name = 'c18.product'
    _description = 'Product (Basic tier - no category/UoM)'
    _order = 'code'

    code = fields.Char(required=True, help='Free-text format, prefix convention determines the grouping (similar to the CoA pattern), not validated by the system.')
    name = fields.Char(required=True)
    product_type = fields.Selection(PRODUCT_TYPES, required=True, default='barang_stok')
    is_purchaseable = fields.Boolean(default=True)
    is_saleable = fields.Boolean(default=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    qty_on_hand = fields.Float(default=0.0, readonly=True)
    avg_cost = fields.Float(default=0.0, readonly=True, help='Running average cost (used when the company costing_method is Average).')
    periodic_purchases_qty = fields.Float(default=0.0, readonly=True,
                                           help='Qty accumulated in the Purchases account since the last periodic Stock Count (Periodic inventory system only).')
    periodic_purchases_value = fields.Float(default=0.0, readonly=True,
                                             help='Value accumulated in the Purchases account since the last periodic Stock Count (Periodic inventory system only).')
    periodic_book_value = fields.Float(default=0.0, readonly=True,
                                        help='Inventory value as of the last periodic Stock Count closing - the "Beginning Inventory" for the next formula (Periodic inventory system only).')

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)', 'Product code must be unique per company.'),
    ]

    def name_get(self):
        return [(rec.id, f'{rec.code} {rec.name}') for rec in self]

    def _stock_receive(self, qty, unit_cost, res_model, res_id, date=None, add_to_purchases_pool=True):
        """Persediaan bertambah (Penerimaan Barang/Retur Customer) - erd/mvp/06 poin F.
        `add_to_purchases_pool` cuma relevan di mode Periodik (poin F.3) - True utk Penerimaan
        Barang (nambah akumulator Pembelian), False utk Retur Customer (barang balik masuk,
        bukan pembelian baru, tanpa efek nilai sama sekali - lihat F.3)."""
        self.ensure_one()
        if self.product_type != 'barang_stok' or qty <= 0:
            return
        if self.company_id.inventory_system == 'periodic':
            self.qty_on_hand += qty
            if add_to_purchases_pool:
                self.periodic_purchases_qty += qty
                self.periodic_purchases_value += qty * unit_cost
            return
        if self.company_id.costing_method == 'fifo':
            self.env['c18.stock.layer'].create({
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
            self._log_average_movement(qty, unit_cost, res_model, res_id, date)

    def _log_average_movement(self, qty, unit_cost, res_model, res_id, date):
        """Audit log costing Average - lihat c18.stock.movement. `qty`
        signed (positif=masuk, negatif=keluar) sesuai konvensi tabel itu."""
        self.env['c18.stock.movement'].create({
            'product_id': self.id, 'date': date or fields.Date.context_today(self),
            'qty': qty, 'unit_cost': unit_cost, 'res_model': res_model, 'res_id': res_id,
        })

    def _consume_layers(self, qty, layers, res_model, res_id, date):
        """Loop konsumsi FIFO bersama dipakai _stock_consume/_stock_consume_latest
        (beda cuma urutan `layers` yang dioper). Tiap layer yang kena konsumsi
        dicatat ke c18.stock.consumption (audit log per-layer per
        transaksi) - dipakai Kartu Stok (erd/mvp/06 poin F) buat split baris
        keluar per layer secara akurat, karena qty_remaining di layer sendiri
        cuma nyimpan state SAAT INI, bukan histori per-transaksi."""
        remaining_to_consume = qty
        total_cost = 0.0
        consumption_vals = []
        for layer in layers:
            if remaining_to_consume <= 0:
                break
            consumed = min(layer.qty_remaining, remaining_to_consume)
            total_cost += consumed * layer.unit_cost
            layer.qty_remaining -= consumed
            remaining_to_consume -= consumed
            consumption_vals.append({
                'product_id': self.id, 'date': date, 'layer_id': layer.id,
                'qty': consumed, 'unit_cost': layer.unit_cost,
                'res_model': res_model, 'res_id': res_id,
            })
        if consumption_vals:
            self.env['c18.stock.consumption'].create(consumption_vals)
        return total_cost

    def _stock_consume(self, qty, res_model=None, res_id=None, date=None):
        """Persediaan berkurang (Pengiriman/Penjualan langsung/Pemakaian Sendiri/Stok Opname).
        Return nilai HPP/beban total dari qty yang dikonsumsi. Stok negatif tidak diperbolehkan.
        `res_model`/`res_id`/`date` opsional (dibutuhkan cuma utk FIFO, dicatat ke audit log
        konsumsi - kalau tidak diisi & costing FIFO, audit log tidak tercatat tapi qty_remaining
        tetap ke-update benar, cuma Kartu Stok baris itu nanti tidak bisa drill-down)."""
        self.ensure_one()
        if self.product_type != 'barang_stok' or qty <= 0:
            return 0.0
        if qty > self.qty_on_hand + 1e-6:
            raise UserError(_('Insufficient stock for %(product)s (available %(available)s, requested %(requested)s).',
                               product=self.name, available=self.qty_on_hand, requested=qty))
        if self.company_id.inventory_system == 'periodic':
            self.qty_on_hand -= qty
            return 0.0
        if self.company_id.costing_method == 'fifo':
            layers = self.env['c18.stock.layer'].search(
                [('product_id', '=', self.id), ('qty_remaining', '>', 0)], order='date, id')
            total_cost = self._consume_layers(qty, layers, res_model, res_id, date or fields.Date.context_today(self))
            self.qty_on_hand -= qty
            return total_cost
        else:
            total_cost = qty * self.avg_cost
            self._log_average_movement(-qty, self.avg_cost, res_model, res_id, date)
            self.qty_on_hand -= qty
            return total_cost

    def _stock_consume_latest(self, qty, res_model=None, res_id=None, date=None):
        """Retur Barang Vendor (erd/mvp/06 poin F.3) - default konsumsi dari layer TERBARU
        (asumsi retur biasanya cepat setelah terima), beda dari _stock_consume yang dari layer
        terlama. Average: sama seperti _stock_consume (avg_cost tidak dipengaruhi arah).
        Mode Periodik: satu-satunya jalur keluar yang TETAP punya nilai (beda dari _stock_consume) -
        reverse dari akumulator Pembelian pakai harga rata-rata pool, krn Retur Vendor
        mengurangi pembelian yang sudah diakui, bukan penjualan/pemakaian (lihat F.3)."""
        self.ensure_one()
        if self.product_type != 'barang_stok' or qty <= 0:
            return 0.0
        if qty > self.qty_on_hand + 1e-6:
            raise UserError(_('Insufficient stock for %(product)s (available %(available)s, requested %(requested)s).',
                               product=self.name, available=self.qty_on_hand, requested=qty))
        if self.company_id.inventory_system == 'periodic':
            rate = (self.periodic_purchases_value / self.periodic_purchases_qty) if self.periodic_purchases_qty else 0.0
            total_cost = qty * rate
            self.periodic_purchases_qty -= qty
            self.periodic_purchases_value -= total_cost
            self.qty_on_hand -= qty
            return total_cost
        if self.company_id.costing_method == 'fifo':
            layers = self.env['c18.stock.layer'].search(
                [('product_id', '=', self.id), ('qty_remaining', '>', 0)], order='date desc, id desc')
            total_cost = self._consume_layers(qty, layers, res_model, res_id, date or fields.Date.context_today(self))
            self.qty_on_hand -= qty
            return total_cost
        else:
            total_cost = qty * self.avg_cost
            self._log_average_movement(-qty, self.avg_cost, res_model, res_id, date)
            self.qty_on_hand -= qty
            return total_cost

    def _last_cost(self):
        """Estimasi harga HPP terakhir - dipakai Retur Barang Customer (E.5) kalau tidak ada
        referensi delivery yang jelas, dan Stok Opname (F.2) selisih positif. Approximation
        (bukan trace exact per-dokumen)."""
        self.ensure_one()
        if self.company_id.costing_method == 'fifo':
            last_layer = self.env['c18.stock.layer'].search(
                [('product_id', '=', self.id)], order='date desc, id desc', limit=1)
            return last_layer.unit_cost if last_layer else 0.0
        return self.avg_cost
