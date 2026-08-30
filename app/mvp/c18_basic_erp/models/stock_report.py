from odoo import api, fields, models

# Label tampilan per res_model - jenis transaksi yang muncul di Kartu Stok.
# Lihat erd/mvp/06-accounting-business.md poin F untuk daftar sumber
# IN/OUT lengkap.
STOCK_CARD_TYPE_LABELS = {
    'c18.purchase.receipt': 'Goods Receipt',
    'c18.sale.return': 'Customer Return',
    'c18.stock.opname': 'Physical Inventory Count',
    'c18.sale.delivery': 'Delivery',
    'c18.sale.invoice': 'Customer Invoice',
    'c18.purchase.return': 'Vendor Return',
    'c18.stock.consume': 'Internal Consumption',
}


class StockReport(models.AbstractModel):
    _name = 'c18.stock.report'
    _description = 'Stock Card Report Data Builder - dipanggil dari controller, bukan model dgn tabel'

    @api.model
    def _fmt(self, amount):
        return '{:,.0f}'.format(amount or 0.0).replace(',', '.')

    @api.model
    def _product_options(self, company):
        return [
            {'value': p.id, 'label': f'{p.code} {p.name}'}
            for p in self.env['c18.product'].search(
                [('company_id', '=', company.id), ('product_type', '=', 'barang_stok')], order='code')
        ]

    @api.model
    def _stock_card_movements(self, product):
        """Kumpulkan semua mutasi (IN+OUT, qty signed: + masuk / - keluar) dari
        sumber yang sesuai `costing_method` company - lihat erd/mvp/06 poin F
        & catatan di stock_consumption.py/stock_movement.py kenapa 2 sumber
        beda dipakai (FIFO vs Average tidak punya struktur data yang sama)."""
        if product.company_id.costing_method == 'fifo':
            in_lines = self.env['c18.stock.layer'].search(
                [('product_id', '=', product.id)], order='date, id')
            out_lines = self.env['c18.stock.consumption'].search(
                [('product_id', '=', product.id)], order='date, id')
            movements = [
                {'date': l.date, 'qty': l.qty_in, 'unit_cost': l.unit_cost,
                 'res_model': l.res_model, 'res_id': l.res_id, 'sort_key': ('layer', l.id)}
                for l in in_lines
            ] + [
                {'date': c.date, 'qty': -c.qty, 'unit_cost': c.unit_cost,
                 'res_model': c.res_model, 'res_id': c.res_id, 'sort_key': ('cons', c.id)}
                for c in out_lines
            ]
        else:
            moves = self.env['c18.stock.movement'].search(
                [('product_id', '=', product.id)], order='date, id')
            movements = [
                {'date': m.date, 'qty': m.qty, 'unit_cost': m.unit_cost,
                 'res_model': m.res_model, 'res_id': m.res_id, 'sort_key': ('mv', m.id)}
                for m in moves
            ]
        movements.sort(key=lambda m: (m['date'], m['sort_key']))
        return movements

    @api.model
    def get_stock_card_data(self, product_id=None, date_from=None, date_to=None):
        """Kartu Stok per produk - erd/mvp/06-accounting-business.md poin F.
        1 laporan = 1 produk (wajib dipilih), pola sama Buku Besar ("1 akun")."""
        company = self.env.company
        Product = self.env['c18.product']
        products = Product.search(
            [('company_id', '=', company.id), ('product_type', '=', 'barang_stok')], order='code')
        product = Product.browse(int(product_id)) if product_id else products[:1]
        if not product:
            return {
                'product_id': False, 'rows': [], 'opening_qty_fmt': self._fmt(0.0),
                'opening_value_fmt': self._fmt(0.0), 'closing_qty_fmt': self._fmt(0.0),
                'closing_value_fmt': self._fmt(0.0),
                'filters': {'product_options': self._product_options(company)},
            }
        product_id = product.id

        today = fields.Date.context_today(self)
        date_from = fields.Date.from_string(date_from) if date_from else today.replace(day=1)
        date_to = fields.Date.from_string(date_to) if date_to else today

        movements = self._stock_card_movements(product)
        opening_qty = sum(m['qty'] for m in movements if m['date'] < date_from)
        opening_value = sum(m['qty'] * m['unit_cost'] for m in movements if m['date'] < date_from)
        period = [m for m in movements if date_from <= m['date'] <= date_to]

        rows = []
        running_qty = opening_qty
        running_value = opening_value
        for m in period:
            running_qty += m['qty']
            running_value += m['qty'] * m['unit_cost']
            doc_name = ''
            if m['res_model'] and m['res_id']:
                record = self.env[m['res_model']].browse(m['res_id'])
                if record.exists():
                    doc_name = record.display_name
            rows.append({
                'date': fields.Date.to_string(m['date']),
                'doc_name': doc_name,
                'res_model': m['res_model'],
                'res_id': m['res_id'],
                'type_label': STOCK_CARD_TYPE_LABELS.get(m['res_model'], m['res_model'] or '-'),
                'qty_in_fmt': self._fmt(m['qty']) if m['qty'] > 0 else '',
                'qty_out_fmt': self._fmt(-m['qty']) if m['qty'] < 0 else '',
                'saldo_qty_fmt': self._fmt(running_qty),
                'unit_cost_fmt': self._fmt(m['unit_cost']),
                'value_in_fmt': self._fmt(m['qty'] * m['unit_cost']) if m['qty'] > 0 else '',
                'value_out_fmt': self._fmt(-m['qty'] * m['unit_cost']) if m['qty'] < 0 else '',
                'saldo_value_fmt': self._fmt(running_value),
            })

        return {
            'product_id': product_id,
            'product_label': f'{product.code} {product.name}',
            'costing_method': company.costing_method,
            'date_from': fields.Date.to_string(date_from),
            'date_to': fields.Date.to_string(date_to),
            'opening_qty_fmt': self._fmt(opening_qty),
            'opening_value_fmt': self._fmt(opening_value),
            'rows': rows,
            'closing_qty_fmt': self._fmt(running_qty),
            'closing_value_fmt': self._fmt(running_value),
            'filters': {'product_options': self._product_options(company)},
        }

    @api.model
    def get_inventory_balance_data(self):
        """Saldo Persediaan - ringkasan qty on hand + nilai per produk saat
        ini (erd/mvp/06 poin F). Total wajib cocok ke saldo akun "1-1300
        Persediaan Barang Dagang" di Trial Balance/Neraca (cross-check)."""
        company = self.env.company
        products = self.env['c18.product'].search(
            [('company_id', '=', company.id), ('product_type', '=', 'barang_stok')], order='code')
        rows = []
        total_value = 0.0
        for product in products:
            if company.currency_id.is_zero(product.qty_on_hand):
                continue
            if company.costing_method == 'fifo':
                layers = self.env['c18.stock.layer'].search(
                    [('product_id', '=', product.id), ('qty_remaining', '>', 0)])
                value = sum(layer.qty_remaining * layer.unit_cost for layer in layers)
            else:
                value = product.qty_on_hand * product.avg_cost
            total_value += value
            rows.append({
                'code': product.code, 'name': product.name,
                'qty_fmt': self._fmt(product.qty_on_hand),
                'value_fmt': self._fmt(value),
            })
        return {
            'costing_method': company.costing_method,
            'rows': rows,
            'total_value_fmt': self._fmt(total_value),
        }
