from odoo import http
from odoo.http import request


class C18StockReportController(http.Controller):

    @http.route('/c18_basic_erp/report/stock_card', type='json', auth='user')
    def stock_card_data(self, product_id=None, date_from=None, date_to=None, **kwargs):
        return request.env['c18.stock.report'].get_stock_card_data(
            product_id=product_id, date_from=date_from, date_to=date_to)

    @http.route('/c18_basic_erp/report/inventory_balance', type='json', auth='user')
    def inventory_balance_data(self, **kwargs):
        return request.env['c18.stock.report'].get_inventory_balance_data()
