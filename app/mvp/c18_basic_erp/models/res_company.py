from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    costing_method = fields.Selection(
        [('fifo', 'FIFO'), ('average', 'Average')],
        default='fifo', required=True,
        help='Inventory costing method, applies uniformly to all Stockable Product items (not per product).')
    inventory_system = fields.Selection(
        [('perpetual', 'Perpetual'), ('periodic', 'Periodic')],
        default='perpetual', required=True,
        help='Perpetual: COGS/Inventory journal posted per transaction (uses costing_method above). '
             'Periodic: COGS calculated once at period-end via Stock Count (Beginning Inventory + Purchases '
             '- Ending Inventory), costing_method (FIFO/Average layers) is not used while this is active.')

    def write(self, vals):
        res = super().write(vals)
        if 'inventory_system' in vals:
            for company in self:
                pembelian = self.env['c18.account.account'].with_context(active_test=False).search(
                    [('code', '=', '5-1100'), ('company_id', '=', company.id)], limit=1)
                if pembelian:
                    pembelian.active = company.inventory_system == 'periodic'
        return res
