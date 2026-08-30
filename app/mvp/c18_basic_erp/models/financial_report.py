import calendar
from collections import defaultdict
from datetime import date, timedelta

from odoo import api, fields, models

# account_type yang tergolong akun Neraca (permanen, saldo kumulatif sejak
# awal - lihat erd/mvp/09-laporan-keuangan.md poin 1) vs Laba Rugi (nominal,
# di-nol-kan tiap tahun via Tutup Buku, saldo kumulatif cuma sejak 1 Jan
# tahun date_to). Dua window beda ini WAJIB - jangan disamakan.
NERACA_TYPES = [
    'cash_bank', 'receivable', 'inventory', 'other_current_asset',
    'fixed_asset', 'other_asset', 'payable', 'other_current_liability',
    'long_term_liability', 'equity',
]
LABA_RUGI_TYPES = ['revenue', 'cost_of_revenue', 'expense', 'other_revenue', 'other_expense']

# Struktur Neraca - erd/mvp/09-laporan-keuangan.md poin 3. "fixed_asset" sengaja
# 1 grup gabungan (bukan dipisah gross vs akumulasi) - Akumulasi Penyusutan
# otomatis netting sendiri karena account_type-nya credit-normal, balance
# (debit-credit) alamiah sudah negatif, jadi ikut ke-total dengan benar tanpa
# logic khusus.
BALANCE_SHEET_SECTIONS = [
    ('aset_lancar', 'Aset Lancar', ['cash_bank', 'receivable', 'inventory', 'other_current_asset']),
    ('aset_tidak_lancar', 'Aset Tidak Lancar', ['fixed_asset', 'other_asset']),
    ('kewajiban_lancar', 'Kewajiban Lancar', ['payable', 'other_current_liability']),
    ('kewajiban_panjang', 'Kewajiban Jangka Panjang', ['long_term_liability']),
    ('ekuitas', 'Ekuitas', ['equity']),
]


class FinancialReport(models.AbstractModel):
    _name = 'c18.account.financial.report'
    _description = 'Financial Report Data Builder - dipanggil dari controller, bukan model dgn tabel'

    @api.model
    def _fmt(self, amount):
        return '{:,.0f}'.format(amount or 0.0).replace(',', '.')

    @api.model
    def _cost_center_options(self, company):
        return [
            {'value': cc.id, 'label': cc.name}
            for cc in self.env['c18.account.cost.center'].search([('company_id', '=', company.id)], order='name')
        ]

    @api.model
    def _account_options(self, company):
        return [
            {'value': acc.id, 'label': f'{acc.code} {acc.name}'}
            for acc in self.env['c18.account.account'].search([('company_id', '=', company.id)], order='code')
        ]

    @api.model
    def _partner_options(self, account_id):
        """Partner yang benar-benar pernah muncul di akun ini - bukan semua
        partner di database (dropdown jadi tidak relevan kalau digabung semua)."""
        Line = self.env['c18.account.move.line']
        grouped = Line._read_group(
            [('account_id', '=', account_id), ('state', '=', 'posted'), ('partner_id', '!=', False)],
            groupby=['partner_id'])
        return sorted(
            [{'value': partner.id, 'label': partner.name} for partner, in grouped],
            key=lambda opt: opt['label'])

    @api.model
    def _trial_balance_balances(self, company, date_to, cost_center_id):
        """Balance per akun pakai aturan window ganda Trial Balance (poin 1) -
        dipakai bareng oleh mode 1-tanggal & mode 12 Bulan, supaya 1 sumber
        rumus (bukan 2 rumus yang harus dijaga sinkron)."""
        year_start = date_to.replace(month=1, day=1)
        balances = {}
        balances.update(self._account_balances(company, NERACA_TYPES, None, date_to, cost_center_id))
        balances.update(self._account_balances(company, LABA_RUGI_TYPES, year_start, date_to, cost_center_id))
        return balances

    @api.model
    def get_trial_balance_data(self, date_to=None, cost_center_id=None, hide_zero=True):
        """Trial Balance (Neraca Saldo) - erd/mvp/09-laporan-keuangan.md poin 1."""
        company = self.env.company
        date_to = fields.Date.from_string(date_to) if date_to else fields.Date.context_today(self)
        cost_center_id = int(cost_center_id) if cost_center_id else False

        accounts = self.env['c18.account.account'].search([('company_id', '=', company.id)], order='code')
        balances = self._trial_balance_balances(company, date_to, cost_center_id)

        rows = []
        total_debit = 0.0
        total_credit = 0.0
        for account in accounts:
            balance = balances.get(account.id, 0.0)
            if hide_zero and company.currency_id.is_zero(balance):
                continue
            debit = balance if balance > 0 else 0.0
            credit = -balance if balance < 0 else 0.0
            total_debit += debit
            total_credit += credit
            rows.append({
                'account_id': account.id,
                'code': account.code,
                'name': account.name,
                'debit_fmt': self._fmt(debit) if debit else '',
                'credit_fmt': self._fmt(credit) if credit else '',
            })

        return {
            'date_to': fields.Date.to_string(date_to),
            'cost_center_id': cost_center_id,
            'hide_zero': hide_zero,
            'company': {'id': company.id, 'name': company.name, 'currency': company.currency_id.name},
            'rows': rows,
            'totals': {
                'debit_fmt': self._fmt(total_debit),
                'credit_fmt': self._fmt(total_credit),
            },
            'mismatch': company.currency_id.compare_amounts(total_debit, total_credit) != 0,
            'filters': {'cost_center_options': self._cost_center_options(company)},
        }

    @api.model
    def get_trial_balance_yearly_data(self, year=None, cost_center_id=None, hide_zero=True):
        """Trial Balance mode 12 Bulan - erd/mvp/09-laporan-keuangan.md poin 1
        "Mode Tampilan 12 Bulan". Tiap kolom bulan = snapshot independen (akun
        Laba Rugi tetap kumulatif sejak 1 Jan sampai akhir bulan kolom itu -
        BUKAN cuma bulan itu, beda dari Laba Rugi 12 Bulan yang independen
        per bulan)."""
        company = self.env.company
        year = int(year) if year else fields.Date.context_today(self).year
        cost_center_id = int(cost_center_id) if cost_center_id else False

        accounts = self.env['c18.account.account'].search([('company_id', '=', company.id)], order='code')
        month_balances = []
        month_totals = []
        for month in range(1, 13):
            date_to = date(year, month, calendar.monthrange(year, month)[1])
            balances = self._trial_balance_balances(company, date_to, cost_center_id)
            month_balances.append(balances)
            month_totals.append({
                'debit': sum(b for b in balances.values() if b > 0),
                'credit': -sum(b for b in balances.values() if b < 0),
            })

        rows = []
        for account in accounts:
            if hide_zero and all(company.currency_id.is_zero(mb.get(account.id, 0.0)) for mb in month_balances):
                continue
            months = []
            for mb in month_balances:
                balance = mb.get(account.id, 0.0)
                months.append({
                    'debit_fmt': self._fmt(balance) if balance > 0 else '',
                    'credit_fmt': self._fmt(-balance) if balance < 0 else '',
                })
            rows.append({'account_id': account.id, 'code': account.code, 'name': account.name, 'months': months})

        return {
            'year': year,
            'cost_center_id': cost_center_id,
            'hide_zero': hide_zero,
            'rows': rows,
            'month_totals': [
                {'debit_fmt': self._fmt(t['debit']), 'credit_fmt': self._fmt(t['credit'])}
                for t in month_totals
            ],
            'filters': {'cost_center_options': self._cost_center_options(company)},
        }

    @api.model
    def get_general_ledger_data(self, account_id=None, date_from=None, date_to=None,
                                 cost_center_id=None, partner_id=None):
        """Buku Besar per akun - erd/mvp/09-laporan-keuangan.md poin 2.

        1 laporan = 1 akun (wajib dipilih) - pola simetris sama Kartu Stok
        ("1 kartu = 1 produk"). Saldo Awal = akumulasi sebelum date_from,
        Saldo Berjalan = kumulatif net (debit - credit) per baris - tanda
        positif berarti condong debit, negatif condong kredit (konsisten
        dengan konvensi tanda yang sama dipakai Trial Balance).
        """
        company = self.env.company
        Account = self.env['c18.account.account']
        accounts = Account.search([('company_id', '=', company.id)], order='code')
        account = Account.browse(int(account_id)) if account_id else accounts[:1]
        if not account:
            return {
                'account_id': False, 'rows': [], 'opening_balance_fmt': self._fmt(0.0),
                'totals': {'debit_fmt': '', 'credit_fmt': '', 'closing_balance_fmt': self._fmt(0.0)},
                'filters': {'account_options': self._account_options(company), 'partner_options': []},
            }
        account_id = account.id

        date_from = fields.Date.from_string(date_from) if date_from else fields.Date.context_today(self).replace(day=1)
        date_to = fields.Date.from_string(date_to) if date_to else fields.Date.context_today(self)
        cost_center_id = int(cost_center_id) if cost_center_id else False
        partner_id = int(partner_id) if partner_id else False

        Line = self.env['c18.account.move.line']
        base_domain = [('account_id', '=', account_id), ('state', '=', 'posted')]
        if cost_center_id:
            base_domain.append(('cost_center_id', '=', cost_center_id))
        if partner_id:
            base_domain.append(('partner_id', '=', partner_id))

        opening_lines = Line.search(base_domain + [('date', '<', date_from)])
        opening_balance = sum(opening_lines.mapped('debit_company_currency')) - sum(opening_lines.mapped('credit_company_currency'))

        period_lines = Line.search(
            base_domain + [('date', '>=', date_from), ('date', '<=', date_to)],
            order='date, id')

        rows = []
        running = opening_balance
        total_debit = 0.0
        total_credit = 0.0
        for line in period_lines:
            debit = line.debit_company_currency
            credit = line.credit_company_currency
            running += debit - credit
            total_debit += debit
            total_credit += credit
            rows.append({
                'date': fields.Date.to_string(line.date),
                'move_id': line.move_id.id,
                'move_name': line.move_id.name,
                'description': line.name or line.move_id.ref or '',
                'partner': line.partner_id.name or '',
                'debit_fmt': self._fmt(debit) if debit else '',
                'credit_fmt': self._fmt(credit) if credit else '',
                'running_balance_fmt': self._fmt(running),
                'res_model': line.res_model or 'c18.account.move',
                'res_id': line.res_id or line.move_id.id,
            })

        return {
            'account_id': account_id,
            'account_label': f'{account.code} {account.name}',
            'date_from': fields.Date.to_string(date_from),
            'date_to': fields.Date.to_string(date_to),
            'cost_center_id': cost_center_id,
            'partner_id': partner_id,
            'opening_balance_fmt': self._fmt(opening_balance),
            'rows': rows,
            'totals': {
                'debit_fmt': self._fmt(total_debit),
                'credit_fmt': self._fmt(total_credit),
                'closing_balance_fmt': self._fmt(running),
            },
            'filters': {
                'account_options': self._account_options(company),
                'partner_options': self._partner_options(account_id),
                'cost_center_options': self._cost_center_options(company),
            },
        }

    @api.model
    def _account_balances(self, company, account_types, date_from, date_to, cost_center_id, exclude_closing=False):
        domain = [
            ('account_id.account_type', 'in', account_types),
            ('account_id.company_id', '=', company.id),
            ('state', '=', 'posted'),
            ('date', '<=', date_to),
        ]
        if date_from:
            domain.append(('date', '>=', date_from))
        if cost_center_id:
            domain.append(('cost_center_id', '=', cost_center_id))
        if exclude_closing:
            # Wajib utk Laba Rugi (erd/mvp/09 poin 4) - jurnal penutup Tutup
            # Buku bakal nolkan Pendapatan/Beban yang sedang dihitung kalau
            # tidak dikecualikan.
            domain.append(('move_id.is_closing_entry', '=', False))
        grouped = self.env['c18.account.move.line']._read_group(
            domain, groupby=['account_id'],
            aggregates=['debit_company_currency:sum', 'credit_company_currency:sum'])
        return {account.id: (debit_sum or 0.0) - (credit_sum or 0.0) for account, debit_sum, credit_sum in grouped}

    @api.model
    def _laba_tahun_berjalan(self, company, date_to):
        """Laba Tahun Berjalan (belum dipindah ke Laba Ditahan) - aturan timing
        di erd/mvp/06-accounting-business.md poin C & 09 poin 3. Return None
        kalau tidak perlu ditampilkan (sudah closed & posted per date_to)."""
        year_start = date_to.replace(month=1, day=1)
        year_end = date_to.replace(month=12, day=31)
        closed = self.env['c18.account.closing'].search([
            ('company_id', '=', company.id), ('fiscal_year', '=', date_to.year), ('state', '=', 'posted'),
        ], limit=1)
        if date_to >= year_end and closed:
            return None
        balances = self._account_balances(company, LABA_RUGI_TYPES, year_start, date_to, False)
        return -sum(balances.values())

    @api.model
    def get_balance_sheet_data(self, date_to=None, cost_center_id=None, hide_zero=True):
        """Neraca (Balance Sheet) - erd/mvp/09-laporan-keuangan.md poin 3."""
        company = self.env.company
        date_to = fields.Date.from_string(date_to) if date_to else fields.Date.context_today(self)
        cost_center_id = int(cost_center_id) if cost_center_id else False

        accounts_by_type = {}
        for account in self.env['c18.account.account'].search([('company_id', '=', company.id)], order='code'):
            accounts_by_type.setdefault(account.account_type, []).append(account)

        all_types = [t for _key, _label, types in BALANCE_SHEET_SECTIONS for t in types]
        balances = self._account_balances(company, all_types, None, date_to, cost_center_id)

        def _build_section(label, types, sign):
            rows = []
            subtotal = 0.0
            for account_type in types:
                for account in accounts_by_type.get(account_type, []):
                    balance = balances.get(account.id, 0.0) * sign
                    if hide_zero and company.currency_id.is_zero(balance):
                        continue
                    subtotal += balance
                    rows.append({'code': account.code, 'name': account.name, 'amount': balance,
                                 'amount_fmt': self._fmt(balance)})
            return {'label': label, 'rows': rows, 'subtotal_fmt': self._fmt(subtotal), 'subtotal': subtotal}

        aset_lancar = _build_section('Aset Lancar', BALANCE_SHEET_SECTIONS[0][2], 1)
        aset_tidak_lancar = _build_section('Aset Tidak Lancar', BALANCE_SHEET_SECTIONS[1][2], 1)
        total_aset = aset_lancar['subtotal'] + aset_tidak_lancar['subtotal']

        kewajiban_lancar = _build_section('Kewajiban Lancar', BALANCE_SHEET_SECTIONS[2][2], -1)
        kewajiban_panjang = _build_section('Kewajiban Jangka Panjang', BALANCE_SHEET_SECTIONS[3][2], -1)
        total_kewajiban = kewajiban_lancar['subtotal'] + kewajiban_panjang['subtotal']

        ekuitas = _build_section('Ekuitas', BALANCE_SHEET_SECTIONS[4][2], -1)
        laba_berjalan = self._laba_tahun_berjalan(company, date_to)
        if laba_berjalan is not None and not (hide_zero and company.currency_id.is_zero(laba_berjalan)):
            ekuitas['rows'].append({'code': '', 'name': 'Laba Tahun Berjalan', 'amount': laba_berjalan,
                                     'amount_fmt': self._fmt(laba_berjalan)})
            ekuitas['subtotal'] += laba_berjalan
            ekuitas['subtotal_fmt'] = self._fmt(ekuitas['subtotal'])
        total_ekuitas = ekuitas['subtotal']

        return {
            'date_to': fields.Date.to_string(date_to),
            'cost_center_id': cost_center_id,
            'company': {'id': company.id, 'name': company.name, 'currency': company.currency_id.name},
            'sections': {
                'aset_lancar': aset_lancar, 'aset_tidak_lancar': aset_tidak_lancar,
                'kewajiban_lancar': kewajiban_lancar, 'kewajiban_panjang': kewajiban_panjang,
                'ekuitas': ekuitas,
            },
            'total_aset_fmt': self._fmt(total_aset),
            'total_aset': total_aset,
            'total_kewajiban_fmt': self._fmt(total_kewajiban),
            'total_ekuitas_fmt': self._fmt(total_ekuitas),
            'total_kewajiban_ekuitas_fmt': self._fmt(total_kewajiban + total_ekuitas),
            'total_kewajiban_ekuitas': total_kewajiban + total_ekuitas,
            'mismatch': company.currency_id.compare_amounts(total_aset, total_kewajiban + total_ekuitas) != 0,
            'filters': {'cost_center_options': self._cost_center_options(company)},
        }

    @api.model
    def get_income_statement_data(self, date_from=None, date_to=None, cost_center_id=None, hide_zero=True):
        """Laba Rugi (Income Statement) - erd/mvp/09-laporan-keuangan.md poin 4.

        `revenue` mencakup akun kontra-revenue "Retur & Potongan Penjualan"
        (sign=-1 sama seperti akun revenue lain) - netting otomatis sama
        seperti fixed_asset/Akumulasi Penyusutan di Neraca, tidak perlu logic
        khusus. WAJIB exclude is_closing_entry.
        """
        company = self.env.company
        today = fields.Date.context_today(self)
        date_from = fields.Date.from_string(date_from) if date_from else today.replace(day=1)
        date_to = fields.Date.from_string(date_to) if date_to else today
        cost_center_id = int(cost_center_id) if cost_center_id else False

        accounts_by_type = {}
        for account in self.env['c18.account.account'].search(
                [('company_id', '=', company.id), ('account_type', 'in', LABA_RUGI_TYPES)], order='code'):
            accounts_by_type.setdefault(account.account_type, []).append(account)

        balances = self._account_balances(company, LABA_RUGI_TYPES, date_from, date_to, cost_center_id,
                                           exclude_closing=True)

        def _section(label, account_type, sign):
            """sign=-1 utk akun credit-normal (revenue/other_revenue, balance
            alamiah negatif kalau ada pendapatan) supaya tampil positif;
            sign=+1 utk akun debit-normal (cost_of_revenue/expense/other_expense)."""
            rows = []
            subtotal = 0.0
            for account in accounts_by_type.get(account_type, []):
                amount = balances.get(account.id, 0.0) * sign
                if hide_zero and company.currency_id.is_zero(amount):
                    continue
                subtotal += amount
                rows.append({'code': account.code, 'name': account.name, 'amount': amount,
                             'amount_fmt': self._fmt(amount)})
            return {'label': label, 'rows': rows, 'subtotal_fmt': self._fmt(subtotal), 'subtotal': subtotal}

        pendapatan = _section('Pendapatan', 'revenue', -1)
        pendapatan_bersih = pendapatan['subtotal']

        hpp = _section('Beban Pokok Pendapatan', 'cost_of_revenue', 1)
        laba_kotor = pendapatan_bersih - hpp['subtotal']

        beban_usaha = _section('Beban Usaha', 'expense', 1)
        laba_usaha = laba_kotor - beban_usaha['subtotal']

        pendapatan_lain = _section('Pendapatan Lain-lain', 'other_revenue', -1)
        beban_lain = _section('Beban Lain-lain', 'other_expense', 1)

        laba_bersih = laba_usaha + pendapatan_lain['subtotal'] - beban_lain['subtotal']

        return {
            'date_from': fields.Date.to_string(date_from),
            'date_to': fields.Date.to_string(date_to),
            'cost_center_id': cost_center_id,
            'sections': {
                'pendapatan': pendapatan, 'hpp': hpp, 'beban_usaha': beban_usaha,
                'pendapatan_lain': pendapatan_lain, 'beban_lain': beban_lain,
            },
            'pendapatan_bersih_fmt': self._fmt(pendapatan_bersih),
            'pendapatan_bersih': pendapatan_bersih,
            'laba_kotor_fmt': self._fmt(laba_kotor),
            'laba_kotor': laba_kotor,
            'laba_usaha_fmt': self._fmt(laba_usaha),
            'laba_usaha': laba_usaha,
            'laba_bersih_fmt': self._fmt(laba_bersih),
            'laba_bersih': laba_bersih,
            'filters': {'cost_center_options': self._cost_center_options(company)},
        }

    # xmlid akun kontrol - erd/mvp/09-laporan-keuangan.md poin 5. Cuma 2 varian
    # (bukan generik semua akun) sesuai keputusan scope: Piutang & Hutang Usaha.
    SUBSIDIARY_LEDGER_ACCOUNTS = {
        'receivable': 'c18_basic_erp.acc_1_1200',
        'payable': 'c18_basic_erp.acc_2_1000',
    }

    @api.model
    def get_subsidiary_ledger_data(self, ledger_type=None, date_to=None, hide_zero=True):
        """Buku Bantu Piutang/Hutang - erd/mvp/09-laporan-keuangan.md poin 5.

        Breakdown per partner dari 1 akun kontrol. sign dibalik utk payable
        supaya tampil positif (akun ini credit-normal).
        """
        company = self.env.company
        ledger_type = ledger_type if ledger_type in self.SUBSIDIARY_LEDGER_ACCOUNTS else 'receivable'
        account = self.env.ref(self.SUBSIDIARY_LEDGER_ACCOUNTS[ledger_type])
        date_to = fields.Date.from_string(date_to) if date_to else fields.Date.context_today(self)
        sign = 1 if ledger_type == 'receivable' else -1

        grouped = self.env['c18.account.move.line']._read_group(
            [('account_id', '=', account.id), ('state', '=', 'posted'), ('date', '<=', date_to)],
            groupby=['partner_id'],
            aggregates=['debit_company_currency:sum', 'credit_company_currency:sum'])

        rows = []
        total = 0.0
        for partner, debit_sum, credit_sum in grouped:
            balance = ((debit_sum or 0.0) - (credit_sum or 0.0)) * sign
            if hide_zero and company.currency_id.is_zero(balance):
                continue
            total += balance
            rows.append({
                'partner_id': partner.id if partner else False,
                'partner_name': partner.name if partner else '(Tanpa Partner)',
                'amount_fmt': self._fmt(balance),
            })
        rows.sort(key=lambda r: r['partner_name'])

        return {
            'ledger_type': ledger_type,
            'account_id': account.id,
            'account_label': f'{account.code} {account.name}',
            'date_to': fields.Date.to_string(date_to),
            'rows': rows,
            'total_fmt': self._fmt(total),
        }

    AGING_BUCKETS = [
        ('current', 0, 0), ('d1_30', 1, 30), ('d31_60', 31, 60),
        ('d61_90', 61, 90), ('d90_plus', 91, None),
    ]

    @api.model
    def get_aging_report_data(self, aging_type=None, date_to=None, hide_zero=True):
        """Umur Piutang/Hutang - bucket per partner dari dokumen yang masih
        outstanding (amount_residual > 0), BUKAN dari move line - tidak ada
        cara melacak move line balik ke invoice/bill mana yang masih terbuka
        selain res_model/res_id generik, dan amount_residual per dokumen
        sudah dijaga akurat oleh Customer Receipt/Vendor Payment.

        Tidak ada field due_date tersimpan di mana pun - dihitung dari
        date dokumen + res_partner.payment_term_days.
        """
        company = self.env.company
        aging_type = aging_type if aging_type in self.SUBSIDIARY_LEDGER_ACCOUNTS else 'receivable'
        model = 'c18.sale.invoice' if aging_type == 'receivable' else 'c18.purchase.bill'
        account = self.env.ref(self.SUBSIDIARY_LEDGER_ACCOUNTS[aging_type])
        date_to = fields.Date.from_string(date_to) if date_to else fields.Date.context_today(self)

        docs = self.env[model].search([
            ('state', '=', 'posted'),
            ('date', '<=', date_to),
            ('amount_residual', '>', 0),
        ])

        buckets = defaultdict(lambda: {key: 0.0 for key, _lo, _hi in self.AGING_BUCKETS})
        for doc in docs:
            due_date = doc.date + timedelta(days=doc.partner_id.payment_term_days)
            days_overdue = (date_to - due_date).days
            for key, lo, hi in self.AGING_BUCKETS:
                if days_overdue >= lo and (hi is None or days_overdue <= hi):
                    buckets[doc.partner_id][key] += doc.amount_residual
                    break

        rows = []
        totals = {key: 0.0 for key, _lo, _hi in self.AGING_BUCKETS}
        totals['total'] = 0.0
        for partner, b in buckets.items():
            row_total = sum(b.values())
            if hide_zero and company.currency_id.is_zero(row_total):
                continue
            for key in b:
                totals[key] += b[key]
            totals['total'] += row_total
            rows.append({
                'partner_id': partner.id,
                'partner_name': partner.name,
                'account_id': account.id,
                **{f'{key}_fmt': self._fmt(v) for key, v in b.items()},
                'total_fmt': self._fmt(row_total),
            })
        rows.sort(key=lambda r: r['partner_name'])

        return {
            'aging_type': aging_type,
            'date_to': fields.Date.to_string(date_to),
            'rows': rows,
            'totals': {key: self._fmt(v) for key, v in totals.items()},
        }

    @api.model
    def get_analysis_report_data(self, analysis_type=None, group_by=None, date_from=None, date_to=None):
        """Sales/Purchase Analysis - rekap qty & nilai dari invoice/bill line
        yang posted (angka tertagih, sejalan dengan konvensi laporan lain di
        modul ini yang bersumber dari move line posted, bukan dari SO/PO draft),
        dikelompokkan per Customer/Vendor, Produk, atau Periode (bulanan).
        """
        analysis_type = analysis_type if analysis_type in ('sales', 'purchase') else 'sales'
        group_by = group_by if group_by in ('partner', 'product', 'period') else 'partner'
        line_model = 'c18.sale.invoice.line' if analysis_type == 'sales' else 'c18.purchase.bill.line'
        parent_field = 'invoice_id' if analysis_type == 'sales' else 'bill_id'
        today = fields.Date.context_today(self)
        date_from = fields.Date.from_string(date_from) if date_from else today.replace(month=1, day=1)
        date_to = fields.Date.from_string(date_to) if date_to else today

        lines = self.env[line_model].search([
            (f'{parent_field}.state', '=', 'posted'),
            (f'{parent_field}.date', '>=', date_from),
            (f'{parent_field}.date', '<=', date_to),
        ])

        agg = defaultdict(lambda: {'qty': 0.0, 'amount': 0.0})
        labels = {}
        for line in lines:
            parent = line[parent_field]
            if group_by == 'partner':
                key = parent.partner_id.id
                labels[key] = parent.partner_id.name
            elif group_by == 'product':
                key = line.product_id.id
                labels[key] = f'{line.product_id.code} {line.product_id.name}' if line.product_id else '(No Product)'
            else:  # period
                key = f'{parent.date.year}-{parent.date.month:02d}'
                labels[key] = key
            agg[key]['qty'] += line.qty
            agg[key]['amount'] += line.subtotal

        rows = []
        total_qty = 0.0
        total_amount = 0.0
        for key, vals in agg.items():
            total_qty += vals['qty']
            total_amount += vals['amount']
            rows.append({
                'key': key,
                'label': labels[key],
                'qty': vals['qty'],
                'amount_fmt': self._fmt(vals['amount']),
            })
        rows.sort(key=lambda r: r['key'] if group_by == 'period' else r['label'])

        return {
            'analysis_type': analysis_type,
            'group_by': group_by,
            'date_from': fields.Date.to_string(date_from),
            'date_to': fields.Date.to_string(date_to),
            'rows': rows,
            'total_qty': total_qty,
            'total_amount_fmt': self._fmt(total_amount),
        }

    @api.model
    def get_equity_changes_data(self, date_from=None, date_to=None):
        """Laporan Perubahan Ekuitas (PSAK 1) - erd/mvp/09-laporan-keuangan.md poin 6.

        3 kolom sesuai CoA yang ada: Modal, Laba Ditahan, Dividen. Baris "Laba
        (Rugi) Periode Berjalan" REUSE angka dari get_income_statement_data -
        jangan hitung ulang pakai rumus terpisah (1 sumber kebenaran).
        Catatan keterbatasan: kalau ada Tutup Buku yang closing entry-nya
        jatuh DI DALAM rentang date_from-date_to yang dipilih, baris "Laba
        Ditahan" bisa tidak cross-check pas ke Neraca (closing entry ikut
        kehitung dobel - sekali lewat pergerakan ledger asli, sekali lagi
        lewat baris Laba Periode). Kasus umum (periode tidak melintasi Tutup
        Buku) aman.
        """
        company = self.env.company
        today = fields.Date.context_today(self)
        date_from = fields.Date.from_string(date_from) if date_from else today.replace(month=1, day=1)
        date_to = fields.Date.from_string(date_to) if date_to else today

        modal = self.env.ref('c18_basic_erp.acc_3_1000')
        laba_ditahan = self.env.ref('c18_basic_erp.acc_3_1100')
        dividen = self.env.ref('c18_basic_erp.acc_3_1300')
        columns = [('modal', modal), ('laba_ditahan', laba_ditahan), ('dividen', dividen)]

        def _balance(account, date_lo, date_hi):
            domain = [('account_id', '=', account.id), ('state', '=', 'posted'), ('date', '<=', date_hi)]
            if date_lo:
                domain.append(('date', '>=', date_lo))
            lines = self.env['c18.account.move.line'].search(domain)
            # sign -1: akun ekuitas credit-normal, tampil positif kalau net kredit
            return -(sum(lines.mapped('debit_company_currency')) - sum(lines.mapped('credit_company_currency')))

        opening = {key: _balance(acc, None, date_from - timedelta(days=1)) for key, acc in columns}
        modal_movement = _balance(modal, date_from, date_to)
        dividen_movement = _balance(dividen, date_from, date_to)
        laba_periode = self.get_income_statement_data(
            date_from=fields.Date.to_string(date_from), date_to=fields.Date.to_string(date_to),
            hide_zero=False)['laba_bersih']

        closing = {
            'modal': opening['modal'] + modal_movement,
            'laba_ditahan': opening['laba_ditahan'] + laba_periode,
            'dividen': opening['dividen'] + dividen_movement,
        }
        closing['total'] = closing['modal'] + closing['laba_ditahan'] + closing['dividen']
        opening_total = opening['modal'] + opening['laba_ditahan'] + opening['dividen']

        def _row(label, modal_v, laba_v, dividen_v):
            total_v = (modal_v or 0.0) + (laba_v or 0.0) + (dividen_v or 0.0)
            return {
                'label': label,
                'modal_fmt': self._fmt(modal_v) if modal_v is not None else '–',
                'laba_ditahan_fmt': self._fmt(laba_v) if laba_v is not None else '–',
                'dividen_fmt': self._fmt(dividen_v) if dividen_v is not None else '–',
                'total_fmt': self._fmt(total_v),
            }

        rows = [
            _row('Saldo Awal', opening['modal'], opening['laba_ditahan'], opening['dividen']),
            _row('Setoran/Penarikan Modal', modal_movement, None, None),
            _row('Laba (Rugi) Periode Berjalan', None, laba_periode, None),
            _row('Dividen/Prive Diumumkan', None, None, dividen_movement),
        ]
        closing_row = _row('Saldo Akhir', closing['modal'], closing['laba_ditahan'], closing['dividen'])

        return {
            'date_from': fields.Date.to_string(date_from),
            'date_to': fields.Date.to_string(date_to),
            'rows': rows,
            'closing_row': closing_row,
        }

    @api.model
    def get_balance_sheet_yearly_data(self, year=None, cost_center_id=None, hide_zero=True):
        """Neraca mode 12 Bulan - erd/mvp/09-laporan-keuangan.md poin 3 "Mode
        Tampilan 12 Bulan". Reuse get_balance_sheet_data() 12x (bukan hitung
        ulang rumusnya) dgn hide_zero=False internal supaya urutan/isi baris
        SAMA persis tiap bulan (gampang di-merge per kode akun), baru filter
        hide_zero di level tahunan (skip baris kalau semua 12 bulan nol)."""
        company = self.env.company
        year = int(year) if year else fields.Date.context_today(self).year
        cost_center_id = int(cost_center_id) if cost_center_id else False

        months_data = []
        for month in range(1, 13):
            date_to = date(year, month, calendar.monthrange(year, month)[1])
            months_data.append(self.get_balance_sheet_data(
                date_to=fields.Date.to_string(date_to), cost_center_id=cost_center_id, hide_zero=False))

        section_keys = ['aset_lancar', 'aset_tidak_lancar', 'kewajiban_lancar', 'kewajiban_panjang', 'ekuitas']
        sections = {}
        for key in section_keys:
            # union kode+nama akun lintas 12 bulan (biasanya identik krn hide_zero=False,
            # tapi "Laba Tahun Berjalan" bisa hilang di bulan Des kalau Tutup Buku sudah
            # posted - makanya tetap union, bukan asumsi baris pertama = master).
            seen = {}
            for md in months_data:
                for row in md['sections'][key]['rows']:
                    seen.setdefault((row['code'], row['name']), None)
            rows = []
            for (code, name) in seen:
                month_amounts = []
                for md in months_data:
                    match = next((r for r in md['sections'][key]['rows'] if r['code'] == code and r['name'] == name), None)
                    month_amounts.append(match['amount'] if match else 0.0)
                if hide_zero and all(company.currency_id.is_zero(a) for a in month_amounts):
                    continue
                rows.append({
                    'code': code, 'name': name,
                    'months_fmt': [self._fmt(a) for a in month_amounts],
                })
            subtotal_per_month = [self._fmt(md['sections'][key]['subtotal']) for md in months_data]
            sections[key] = {'label': months_data[0]['sections'][key]['label'], 'rows': rows,
                              'subtotal_months_fmt': subtotal_per_month}

        return {
            'year': year,
            'cost_center_id': cost_center_id,
            'hide_zero': hide_zero,
            'sections': sections,
            'total_aset_months_fmt': [self._fmt(md['total_aset']) for md in months_data],
            'total_kewajiban_ekuitas_months_fmt': [self._fmt(md['total_kewajiban_ekuitas']) for md in months_data],
            'mismatch_months': [md['mismatch'] for md in months_data],
            'filters': {'cost_center_options': self._cost_center_options(company)},
        }

    @api.model
    def get_income_statement_yearly_data(self, year=None, cost_center_id=None, hide_zero=True):
        """Laba Rugi mode 12 Bulan - erd/mvp/09-laporan-keuangan.md poin 4
        "Mode Tampilan 12 Bulan". BEDA dari Neraca/Trial Balance 12 Bulan:
        tiap kolom bulan INDEPENDEN (bukan kumulatif) - reuse
        get_income_statement_data() per bulan (rentang 1 bulan sendiri) +
        1x lagi utk rentang setahun penuh (kolom "Total (YTD)")."""
        company = self.env.company
        year = int(year) if year else fields.Date.context_today(self).year
        cost_center_id = int(cost_center_id) if cost_center_id else False

        months_data = []
        for month in range(1, 13):
            date_from = date(year, month, 1)
            date_to = date(year, month, calendar.monthrange(year, month)[1])
            months_data.append(self.get_income_statement_data(
                date_from=fields.Date.to_string(date_from), date_to=fields.Date.to_string(date_to),
                cost_center_id=cost_center_id, hide_zero=False))
        total_data = self.get_income_statement_data(
            date_from=fields.Date.to_string(date(year, 1, 1)), date_to=fields.Date.to_string(date(year, 12, 31)),
            cost_center_id=cost_center_id, hide_zero=False)
        all_periods = months_data + [total_data]

        section_keys = ['pendapatan', 'hpp', 'beban_usaha', 'pendapatan_lain', 'beban_lain']
        sections = {}
        for key in section_keys:
            seen = {}
            for pd in all_periods:
                for row in pd['sections'][key]['rows']:
                    seen.setdefault((row['code'], row['name']), None)
            rows = []
            for (code, name) in seen:
                amounts = []
                for pd in all_periods:
                    match = next((r for r in pd['sections'][key]['rows'] if r['code'] == code and r['name'] == name), None)
                    amounts.append(match['amount'] if match else 0.0)
                if hide_zero and all(company.currency_id.is_zero(a) for a in amounts):
                    continue
                rows.append({'code': code, 'name': name, 'amounts_fmt': [self._fmt(a) for a in amounts]})
            sections[key] = {
                'label': all_periods[0]['sections'][key]['label'],
                'rows': rows,
                'subtotal_fmt': [self._fmt(pd['sections'][key]['subtotal']) for pd in all_periods],
            }

        return {
            'year': year,
            'cost_center_id': cost_center_id,
            'hide_zero': hide_zero,
            'sections': sections,
            'pendapatan_bersih_fmt': [self._fmt(pd['pendapatan_bersih']) for pd in all_periods],
            'laba_kotor_fmt': [self._fmt(pd['laba_kotor']) for pd in all_periods],
            'laba_usaha_fmt': [self._fmt(pd['laba_usaha']) for pd in all_periods],
            'laba_bersih_fmt': [self._fmt(pd['laba_bersih']) for pd in all_periods],
            'filters': {'cost_center_options': self._cost_center_options(company)},
        }
