from odoo import api, models

# (label, model, extra domain, action xmlid) per baris - urutan & pengelompokan
# ikut persis urutan menu di menu.xml, supaya breakdown dashboard konsisten
# dengan yang dilihat user di sidebar.
DASHBOARD_SECTIONS = [
    ('accounting', 'Accounting', [
        ('General Journal', 'c18.account.move', [('journal_id.code', '=', 'JU')], 'c18_basic_erp.action_c18_basic_erp_move'),
        ('Beginning of Year Adjustment', 'c18.account.move', [('journal_id.code', '=', 'PAWL')], 'c18_basic_erp.action_c18_basic_erp_move_pawl'),
        ('End of Year Adjustment', 'c18.account.move', [('journal_id.code', '=', 'PAKH')], 'c18_basic_erp.action_c18_basic_erp_move_pakh'),
        ('Period Closing', 'c18.account.closing', [], 'c18_basic_erp.action_c18_basic_erp_closing'),
        ('Cash In', 'c18.account.cash', [('journal_id.code', '=', 'KM')], 'c18_basic_erp.action_c18_basic_erp_cash_in'),
        ('Cash Out', 'c18.account.cash', [('journal_id.code', '=', 'KK')], 'c18_basic_erp.action_c18_basic_erp_cash_out'),
        ('Cash/Bank Transfer', 'c18.account.cash', [('journal_id.code', '=', 'TRF')], 'c18_basic_erp.action_c18_basic_erp_cash_transfer'),
    ]),
    ('purchase', 'Purchase', [
        ('Purchase Order', 'c18.purchase.order', [], 'c18_basic_erp.action_c18_purchase_order'),
        ('Goods Receipt', 'c18.purchase.receipt', [], 'c18_basic_erp.action_c18_purchase_receipt'),
        ('Vendor Bill', 'c18.purchase.bill', [], 'c18_basic_erp.action_c18_purchase_bill'),
        ('Purchase Advance', 'c18.purchase.advance', [], 'c18_basic_erp.action_c18_purchase_advance'),
        ('Vendor Payment', 'c18.purchase.payment', [], 'c18_basic_erp.action_c18_purchase_payment'),
        ('Vendor Return', 'c18.purchase.return', [], 'c18_basic_erp.action_c18_purchase_return'),
        ('Accounts Payable Write-off', 'c18.purchase.writeoff', [], 'c18_basic_erp.action_c18_purchase_writeoff'),
    ]),
    ('sales', 'Sales', [
        ('Sales Order', 'c18.sale.order', [], 'c18_basic_erp.action_c18_sale_order'),
        ('Delivery', 'c18.sale.delivery', [], 'c18_basic_erp.action_c18_sale_delivery'),
        ('Customer Invoice', 'c18.sale.invoice', [], 'c18_basic_erp.action_c18_sale_invoice'),
        ('Sales Advance', 'c18.sale.advance', [], 'c18_basic_erp.action_c18_sale_advance'),
        ('Customer Receipt', 'c18.sale.receipt', [], 'c18_basic_erp.action_c18_sale_receipt'),
        ('Customer Return', 'c18.sale.return', [], 'c18_basic_erp.action_c18_sale_return'),
        ('Accounts Receivable Write-off', 'c18.sale.writeoff', [], 'c18_basic_erp.action_c18_sale_writeoff'),
    ]),
    ('inventory', 'Inventory', [
        ('Internal Consumption', 'c18.stock.consume', [], 'c18_basic_erp.action_c18_basic_erp_stock_consume'),
        ('Physical Inventory Count', 'c18.stock.opname', [], 'c18_basic_erp.action_c18_basic_erp_stock_opname'),
    ]),
    ('payroll', 'Payroll', [
        ('Accrual Entry', 'c18.payroll.accrual', [], 'c18_basic_erp.action_c18_payroll_accrual'),
        ('Payment Entry', 'c18.payroll.payment', [], 'c18_basic_erp.action_c18_payroll_payment'),
    ]),
    ('fixed_asset', 'Fixed Asset', [
        ('Fixed Asset', 'c18.fixed.asset.entry', [], 'c18_basic_erp.action_c18_fixed_asset_entry'),
    ]),
]


class Dashboard(models.AbstractModel):
    _name = 'c18.basic.erp.dashboard'
    _description = 'Home Dashboard Counts - dipanggil dari controller, bukan model dgn tabel'

    @api.model
    def _count(self, model, domain):
        return self.env[model].search_count(domain + [('company_id', '=', self.env.company.id)])

    @api.model
    def get_dashboard_counts(self):
        return {
            key: {
                'label': label,
                'items': [
                    {'label': item_label, 'count': self._count(model, domain), 'action': action}
                    for item_label, model, domain, action in items
                ],
            }
            for key, label, items in DASHBOARD_SECTIONS
        }
