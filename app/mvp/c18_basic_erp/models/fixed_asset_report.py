from odoo import _, fields, models


class FixedAssetReportWizard(models.TransientModel):
    _name = 'c18.fixed.asset.report.wizard'
    _description = (
        'Laporan Daftar Aktiva Tetap (tier Basic) - murni rekap SUM dari jurnal '
        'manual per kode_aset, bukan hasil kalkulasi otomatis. Lihat '
        'notes/human-notes/fitur-laporan.txt baris 19 & '
        'erd/mvp/06-accounting-business.md poin G.'
    )

    date_from = fields.Date(required=True, default=lambda self: fields.Date.context_today(self).replace(month=1, day=1))
    date_to = fields.Date(required=True, default=fields.Date.context_today)
    line_ids = fields.One2many('c18.fixed.asset.report.line', 'wizard_id', readonly=True)
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    total_harga_perolehan = fields.Monetary(string='Total Harga Perolehan (Daftar Aktiva)', readonly=True)
    total_saldo_coa = fields.Monetary(string='Total Saldo Akun Aktiva Tetap (COA)', readonly=True)
    is_mismatch = fields.Boolean(readonly=True)
    mismatch_message = fields.Char(readonly=True)

    def _check_reconciliation(self):
        """Wrapper tipis di atas c18.fixed.asset.entry._check_coa_reconciliation()
        (logic sama dipakai juga saat action_post entry, biar tidak duplikasi
        query) - simpan hasilnya ke field wizard buat ditampilkan di form."""
        self.ensure_one()
        total_register, total_coa, mismatch = self.env['c18.fixed.asset.entry']._check_coa_reconciliation(
            date_to=self.date_to)
        self.total_harga_perolehan = total_register
        self.total_saldo_coa = total_coa
        self.is_mismatch = mismatch
        self.mismatch_message = _(
            'Total harga perolehan di Daftar Aktiva (%(register)s) TIDAK SAMA dengan total saldo '
            'debit akun bertipe Aktiva Tetap di COA (%(coa)s) - kemungkinan ada jurnal yang '
            'posting langsung ke akun Aktiva Tetap tanpa lewat form Aktiva Tetap/tanpa Kode Aset.',
            register=total_register, coa=total_coa,
        ) if mismatch else False

    def action_generate(self):
        self.ensure_one()
        entries = self.env['c18.fixed.asset.entry'].search([
            ('state', '=', 'posted'),
            ('asset_tag_id', '!=', False),
            ('date', '<=', self.date_to),
        ])
        lines = []
        for tag in entries.asset_tag_id:
            tag_entries = entries.filtered(lambda e, tag=tag: e.asset_tag_id == tag)
            pengakuan = tag_entries.filtered(lambda e: e.transaction_type == 'pengakuan')
            penyusutan_awal = tag_entries.filtered(
                lambda e, self=self: e.transaction_type == 'penyusutan' and e.date < self.date_from)
            penyusutan_periode = tag_entries.filtered(
                lambda e, self=self: e.transaction_type == 'penyusutan' and self.date_from <= e.date <= self.date_to)
            harga_perolehan = sum(pengakuan.mapped('amount'))
            akumulasi_awal = sum(penyusutan_awal.mapped('amount'))
            beban_periode = sum(penyusutan_periode.mapped('amount'))
            akumulasi_akhir = akumulasi_awal + beban_periode
            lines.append((0, 0, {
                'asset_tag_id': tag.id,
                'tanggal_perolehan': min(pengakuan.mapped('date')) if pengakuan else False,
                'harga_perolehan': harga_perolehan,
                'akumulasi_awal': akumulasi_awal,
                'beban_periode': beban_periode,
                'akumulasi_akhir': akumulasi_akhir,
                'nilai_buku': harga_perolehan - akumulasi_akhir,
            }))
        self.line_ids = [(5, 0, 0)] + lines
        self._check_reconciliation()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'current',
        }


class FixedAssetReportLine(models.TransientModel):
    _name = 'c18.fixed.asset.report.line'
    _description = 'Baris Laporan Daftar Aktiva Tetap'
    _order = 'asset_tag_id'

    wizard_id = fields.Many2one('c18.fixed.asset.report.wizard', required=True, ondelete='cascade')
    asset_tag_id = fields.Many2one('c18.fixed.asset.tag', string='Kode Aset', required=True)
    tanggal_perolehan = fields.Date(string='Tanggal Perolehan')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)
    harga_perolehan = fields.Monetary(string='Harga Perolehan')
    akumulasi_awal = fields.Monetary(string='Akumulasi Penyusutan Awal Periode')
    beban_periode = fields.Monetary(string='Beban Penyusutan Periode Ini')
    akumulasi_akhir = fields.Monetary(string='Akumulasi Penyusutan Akhir Periode')
    nilai_buku = fields.Monetary(string='Nilai Buku')
