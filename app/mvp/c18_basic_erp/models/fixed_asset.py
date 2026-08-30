from odoo import _, api, fields, models
from odoo.exceptions import UserError

TRANSACTION_TYPES = [
    ('pengakuan', 'Acquisition'),
    ('penyusutan', 'Depreciation'),
    ('penghapusan', 'Disposal'),
    ('penjualan', 'Sale'),
    ('revaluasi', 'Revaluation'),
]

JOURNAL_XMLID_BY_TYPE = {
    'pengakuan': 'c18_basic_erp.journal_akat',
    'penyusutan': 'c18_basic_erp.journal_pnyt',
    'penghapusan': 'c18_basic_erp.journal_haps',
    'penjualan': 'c18_basic_erp.journal_jlat',
    'revaluasi': 'c18_basic_erp.journal_rvls',
}


class FixedAssetTag(models.Model):
    _name = 'c18.fixed.asset.tag'
    _description = (
        'Asset Code - lightweight tag to group Fixed Asset transactions per asset '
        '(not a full asset register, no category/useful life/depreciation '
        'calculation - see erd/mvp/06-accounting-business.md point G)'
    )
    _order = 'code'

    code = fields.Char(string='Code', required=True)
    name = fields.Char(string='Asset Name', required=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)

    _sql_constraints = [
        ('code_company_uniq', 'unique(code, company_id)', 'Asset code is already in use.'),
    ]

    def name_get(self):
        return [(rec.id, f'{rec.code} - {rec.name}') for rec in self]


class FixedAsset(models.Model):
    _name = 'c18.fixed.asset.entry'
    _description = 'Fixed Asset (Basic tier - generic form, no asset register)'
    _order = 'date desc, id desc'

    name = fields.Char(default='New', copy=False, readonly=True, string='Number')
    date = fields.Date(required=True, default=fields.Date.context_today)
    transaction_type = fields.Selection(TRANSACTION_TYPES, required=True, default='pengakuan')
    asset_tag_id = fields.Many2one(
        'c18.fixed.asset.tag', string='Asset Code',
        help='Grouping key for the Fixed Asset Register report - pick from the existing list, not free text.')
    debit_account_id = fields.Many2one('c18.account.account', string='Debit Account', required=True)
    credit_account_id = fields.Many2one('c18.account.account', string='Credit Account', required=True)
    partner_id = fields.Many2one('res.partner')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    amount = fields.Monetary(currency_field='currency_id', required=True)
    note = fields.Char(string='Notes')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    exchange_rate = fields.Float(
        digits=(12, 6), default=1.0,
        help='Exchange rate at the time of the transaction (erd/mvp/01 point 5) - same as c18.account.move.exchange_rate, '
             'used when generating the journal entry so reconciliation to the COA is correct when currency_id is not the company currency.')
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', copy=False, required=True)
    move_id = fields.Many2one('c18.account.move', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for rec in records:
            if rec.name == 'New':
                rec.name = f'draft-{rec.id}'
        return records

    def _check_coa_reconciliation(self, date_to=False):
        """Bandingkan total harga perolehan (Pengakuan) di register vs total
        debit GL akun tipe Aktiva Tetap - dipanggil tiap kali ada aktivitas
        posting di modul ini (bukan cuma pas buka laporan), supaya mismatch
        (mis. ada jurnal yang bypass form ini lewat Jurnal Umum) langsung
        ternotice. Dipakai juga oleh c18.fixed.asset.report.wizard. Lihat
        erd/mvp/06-accounting-business.md poin G. Return (total_register,
        total_coa, mismatch)."""
        company = self.env.company
        date_to = date_to or fields.Date.context_today(self)
        entries = self.env['c18.fixed.asset.entry'].search([
            ('state', '=', 'posted'),
            ('transaction_type', '=', 'pengakuan'),
            ('company_id', '=', company.id),
            ('date', '<=', date_to),
        ])
        # Konversi ke company currency dulu (erd/mvp/01 poin 5) - jangan jumlah
        # amount/debit mentah, bisa campur currency lintas entry/jurnal.
        total_register = sum(e.amount * (e.exchange_rate or 1.0) for e in entries)
        gl_lines = self.env['c18.account.move.line'].search([
            ('account_id.account_type', '=', 'fixed_asset'),
            ('company_id', '=', company.id),
            ('state', '=', 'posted'),
            ('date', '<=', date_to),
            ('debit', '>', 0),
        ])
        total_coa = sum(gl_lines.mapped('debit_company_currency'))
        mismatch = company.currency_id.compare_amounts(total_register, total_coa) != 0
        return total_register, total_coa, mismatch

    def action_post(self):
        for rec in self:
            if rec.state != 'draft':
                continue
            if not rec.amount:
                raise UserError(_('Amount is required.'))
            # Harga perolehan (Pengakuan) wajib nyambung ke akun tipe Aktiva
            # Tetap & wajib ada asset_tag_id - supaya total di laporan Daftar
            # Aktiva Tetap otomatis cocok dengan saldo akun Aktiva Tetap di
            # Neraca (bukan dicek belakangan, tapi dicegah dari titik posting).
            # Lihat erd/mvp/06-accounting-business.md poin G.
            if rec.transaction_type == 'pengakuan':
                if not rec.asset_tag_id:
                    raise UserError(_('Asset Code is required for Acquisition transactions.'))
                if rec.debit_account_id.account_type != 'fixed_asset':
                    raise UserError(_('The Debit Account for an Acquisition must be a Fixed Assets type account.'))
            journal = self.env.ref(JOURNAL_XMLID_BY_TYPE[rec.transaction_type])
            move = self.env['c18.account.move'].create({
                'journal_id': journal.id,
                'date': rec.date,
                'ref': rec.note or rec.name,
                'company_id': rec.company_id.id,
                'currency_id': rec.currency_id.id,
                'exchange_rate': rec.exchange_rate,
                'line_ids': [
                    (0, 0, {
                        'account_id': rec.debit_account_id.id,
                        'debit': rec.amount,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                    (0, 0, {
                        'account_id': rec.credit_account_id.id,
                        'credit': rec.amount,
                        'partner_id': rec.partner_id.id,
                        'cost_center_id': rec.cost_center_id.id,
                    }),
                ],
            })
            move.line_ids.write({'res_model': rec._name, 'res_id': rec.id})
            move.action_post()
            rec.write({'move_id': move.id, 'name': move.name, 'state': 'posted'})

        total_register, total_coa, mismatch = self._check_coa_reconciliation()
        if mismatch:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Warning: Fixed Assets Not Reconciled'),
                    'message': _(
                        'The total acquisition cost in the register (%(register)s) does NOT MATCH the total '
                        'debit balance of Fixed Assets type accounts in the COA (%(coa)s) - check Reports > '
                        'Fixed Asset Register.', register=total_register, coa=total_coa,
                    ),
                    'type': 'warning',
                    'sticky': True,
                },
            }
