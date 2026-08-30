from odoo import http
from odoo.http import request


class C18FinancialReportController(http.Controller):
    # auth='user' cukup - ir.model.access.csv modul ini tidak punya group_id
    # restriction sama sekali (semua user internal punya akses penuh), jadi
    # tidak ada group spesifik yang perlu dicek di sini (beda dari pola
    # PAYROLL_GROUP di referensi odoo18_toso). Kalau nanti ada security group
    # khusus report keuangan, cek grup itu di sini juga.

    @http.route('/c18_basic_erp/report/trial_balance', type='json', auth='user')
    def trial_balance_data(self, date_to=None, cost_center_id=None, hide_zero=True, **kwargs):
        return request.env['c18.account.financial.report'].get_trial_balance_data(
            date_to=date_to, cost_center_id=cost_center_id, hide_zero=hide_zero)

    @http.route('/c18_basic_erp/report/general_ledger', type='json', auth='user')
    def general_ledger_data(self, account_id=None, date_from=None, date_to=None,
                             cost_center_id=None, partner_id=None, **kwargs):
        return request.env['c18.account.financial.report'].get_general_ledger_data(
            account_id=account_id, date_from=date_from, date_to=date_to,
            cost_center_id=cost_center_id, partner_id=partner_id)

    @http.route('/c18_basic_erp/report/balance_sheet', type='json', auth='user')
    def balance_sheet_data(self, date_to=None, cost_center_id=None, hide_zero=True, **kwargs):
        return request.env['c18.account.financial.report'].get_balance_sheet_data(
            date_to=date_to, cost_center_id=cost_center_id, hide_zero=hide_zero)

    @http.route('/c18_basic_erp/report/income_statement', type='json', auth='user')
    def income_statement_data(self, date_from=None, date_to=None, cost_center_id=None, hide_zero=True, **kwargs):
        return request.env['c18.account.financial.report'].get_income_statement_data(
            date_from=date_from, date_to=date_to, cost_center_id=cost_center_id, hide_zero=hide_zero)

    @http.route('/c18_basic_erp/report/subsidiary_ledger', type='json', auth='user')
    def subsidiary_ledger_data(self, ledger_type=None, date_to=None, hide_zero=True, **kwargs):
        return request.env['c18.account.financial.report'].get_subsidiary_ledger_data(
            ledger_type=ledger_type, date_to=date_to, hide_zero=hide_zero)

    @http.route('/c18_basic_erp/report/equity_changes', type='json', auth='user')
    def equity_changes_data(self, date_from=None, date_to=None, **kwargs):
        return request.env['c18.account.financial.report'].get_equity_changes_data(
            date_from=date_from, date_to=date_to)

    @http.route('/c18_basic_erp/report/trial_balance_yearly', type='json', auth='user')
    def trial_balance_yearly_data(self, year=None, cost_center_id=None, hide_zero=True, **kwargs):
        return request.env['c18.account.financial.report'].get_trial_balance_yearly_data(
            year=year, cost_center_id=cost_center_id, hide_zero=hide_zero)

    @http.route('/c18_basic_erp/report/balance_sheet_yearly', type='json', auth='user')
    def balance_sheet_yearly_data(self, year=None, cost_center_id=None, hide_zero=True, **kwargs):
        return request.env['c18.account.financial.report'].get_balance_sheet_yearly_data(
            year=year, cost_center_id=cost_center_id, hide_zero=hide_zero)

    @http.route('/c18_basic_erp/report/income_statement_yearly', type='json', auth='user')
    def income_statement_yearly_data(self, year=None, cost_center_id=None, hide_zero=True, **kwargs):
        return request.env['c18.account.financial.report'].get_income_statement_yearly_data(
            year=year, cost_center_id=cost_center_id, hide_zero=hide_zero)
