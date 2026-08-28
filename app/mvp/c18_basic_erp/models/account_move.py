from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _name = 'c18.account.move'
    _description = 'Journal Entry'
    _order = 'date desc, id desc'

    name = fields.Char(default='/', copy=False, readonly=True)
    date = fields.Date(required=True, default=fields.Date.context_today)
    journal_id = fields.Many2one('c18.account.journal', required=True)
    ref = fields.Char(string='Referensi/Keterangan')
    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id, required=True)
    exchange_rate = fields.Float(digits=(12, 6), default=1.0,
                                  help='Kurs transaksi saat itu, disimpan permanen (tidak dihitung ulang belakangan).')
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company, required=True)
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted')], default='draft', required=True, copy=False)
    line_ids = fields.One2many('c18.account.move.line', 'move_id', copy=True)
    amount_total = fields.Monetary(compute='_compute_amount_total', currency_field='currency_id')
    is_closing_entry = fields.Boolean(
        default=False, copy=False,
        help='Penanda jurnal penutup dari Tutup Buku (erd/mvp/06 poin C) - dipakai query Laporan '
             'Laba Rugi utk MENGECUALIKAN baris ini, supaya akun Pendapatan/Beban yang dinolkan '
             'tidak ikut kehitung dan bikin laporan salah nunjukin 0.')

    @api.depends('line_ids.debit')
    def _compute_amount_total(self):
        for move in self:
            move.amount_total = sum(move.line_ids.mapped('debit'))

    def _get_locked_date(self, company):
        """Tanggal tutup buku terakhir yang sudah posted - periode <= tanggal ini terkunci
        (erd/mvp/01 poin 6, dirinci di erd/mvp/06 poin C)."""
        closing = self.env['c18.account.closing'].search(
            [('company_id', '=', company.id), ('state', '=', 'posted')], order='closing_date desc', limit=1)
        return closing.closing_date if closing else False

    def _check_period_lock(self, vals_list):
        for vals in vals_list:
            if vals.get('is_closing_entry'):
                continue
            date = vals.get('date')
            company_id = vals.get('company_id') or self.env.company.id
            if not date:
                continue
            locked_date = self._get_locked_date(self.env['res.company'].browse(company_id))
            if locked_date and date <= locked_date:
                raise UserError(_('Periode %(date)s sudah ditutup (Tutup Buku %(locked)s) - tidak bisa tambah/edit jurnal di tanggal itu.',
                                   date=date, locked=locked_date))

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            journal = self.env['c18.account.journal'].browse(vals.get('journal_id')) if vals.get('journal_id') else False
            if journal and vals.get('date'):
                vals['date'] = self._adjust_date_for_journal(journal, vals['date'])
        self._check_period_lock(vals_list)
        return super().create(vals_list)

    def write(self, vals):
        if 'date' in vals and self:
            journal = self.env['c18.account.journal'].browse(vals['journal_id']) if vals.get('journal_id') else self[0].journal_id
            if journal:
                vals['date'] = self._adjust_date_for_journal(journal, vals['date'])
        if 'date' in vals or 'journal_id' in vals:
            for move in self:
                journal = self.env['c18.account.journal'].browse(vals['journal_id']) if vals.get('journal_id') else move.journal_id
                new_date = vals.get('date', move.date)
                if journal and new_date:
                    self._check_period_lock([{'date': new_date, 'company_id': move.company_id.id,
                                               'is_closing_entry': move.is_closing_entry}])
        return super().write(vals)

    @api.model
    def _adjust_date_for_journal(self, journal, date):
        """Penyesuaian Awal Tahun (PAWL) terkunci ke 1 Jan, Penyesuaian Akhir Tahun (PAKH) ke 31 Des
        tahun yang sama dengan tanggal yang dipilih user (erd/mvp/06 poin C)."""
        if isinstance(date, str):
            date = fields.Date.from_string(date)
        if journal.code == 'PAWL':
            date = date.replace(month=1, day=1)
        elif journal.code == 'PAKH':
            date = date.replace(month=12, day=31)
        return date

    def action_post(self):
        for move in self:
            if move.state != 'draft':
                continue
            if not move.line_ids:
                raise UserError(_('Jurnal tidak boleh kosong.'))
            total_debit = sum(move.line_ids.mapped('debit'))
            total_credit = sum(move.line_ids.mapped('credit'))
            if move.company_id.currency_id.compare_amounts(total_debit, total_credit) != 0:
                raise UserError(_('Total debit (%(debit)s) harus sama dengan total kredit (%(credit)s) sebelum posting.',
                                   debit=total_debit, credit=total_credit))
            if move.name == '/':
                move.name = move.journal_id.sequence_id.next_by_id()
            move.state = 'posted'

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})

    def unlink(self):
        for move in self:
            if not move.is_closing_entry:
                locked_date = self._get_locked_date(move.company_id)
                if locked_date and move.date and move.date <= locked_date:
                    raise UserError(_('Periode %(date)s sudah ditutup (Tutup Buku %(locked)s) - tidak bisa hapus jurnal di tanggal itu.',
                                       date=move.date, locked=locked_date))
        return super().unlink()


class AccountMoveLine(models.Model):
    _name = 'c18.account.move.line'
    _description = 'Journal Entry Line'
    _order = 'move_id, sequence, id'

    move_id = fields.Many2one('c18.account.move', required=True, ondelete='cascade')
    sequence = fields.Integer(default=10)
    account_id = fields.Many2one('c18.account.account', required=True)
    partner_id = fields.Many2one('res.partner')
    cost_center_id = fields.Many2one('c18.account.cost.center')
    name = fields.Char(string='Deskripsi')
    debit = fields.Monetary(default=0.0, currency_field='currency_id')
    credit = fields.Monetary(default=0.0, currency_field='currency_id')
    currency_id = fields.Many2one(related='move_id.currency_id', store=True)
    company_id = fields.Many2one(related='move_id.company_id', store=True)
    date = fields.Date(related='move_id.date', store=True)
    state = fields.Selection(related='move_id.state', store=True)

    # Generic reference ke dokumen sumber yang men-generate baris ini (erd/mvp/01 poin 3)
    res_model = fields.Char()
    res_id = fields.Integer()
