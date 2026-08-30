from odoo import http
from odoo.http import request


class C18DashboardController(http.Controller):

    @http.route('/c18_basic_erp/dashboard/counts', type='json', auth='user')
    def dashboard_counts(self, **kwargs):
        return request.env['c18.basic.erp.dashboard'].get_dashboard_counts()
