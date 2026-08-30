# Requirement - Laporan Keuangan: Neraca, Laba Rugi, Perubahan Ekuitas, Trial Balance, Buku Besar, Buku Bantu Piutang/Hutang (`c18_basic_erp` lanjutan, tier Standard+)

Status: **SEMUA 9 laporan/mode SUDAH diimplementasikan & diverifikasi** (2026-08-30) — Trial Balance (1-tanggal + 12 Bulan), Buku Besar, Neraca (1-tanggal + 12 Bulan), Laba Rugi (1-rentang + 12 Bulan), Buku Bantu Piutang/Hutang, Laporan Perubahan Ekuitas — semua saling cross-check dengan benar. Sisa cuma export PDF/Excel (opsional, lihat "Belum Diputuskan"). Melengkapi [06-accounting-business.md poin 3](06-accounting-business.md#3-laporan-keuangan-tier-standard) yang sebelumnya cuma konfirmasi nama 4 laporan tanpa detail field-level — sekarang jadi dokumen sendiri karena scope-nya besar (7 laporan: 4 utama + 2 varian Buku Bantu + Laporan Perubahan Ekuitas). 06 tetap jadi rujukan untuk aturan lintas-laporan yang sudah ada (timing "Laba Tahun Berjalan" di Neraca, baris 66-68).

## Arsitektur Implementasi (final, diputuskan & dipraktikkan 2026-08-30)

Bukan wizard `TransientModel` + tombol "Generate" (rencana awal, sempat ditulis di draft sebelumnya) — setelah user tunjuk contoh report slip gaji interaktif di repo referensi **`odoo18_toso`** (`c18_hr_payroll`), polanya diadopsi penuh:

1. **`models.AbstractModel`** (`c18.account.financial.report`, di `financial_report.py`) — murni class logic, tidak ada tabel DB. Tiap laporan = 1 method (`get_trial_balance_data()`, dst), return dict JSON-serializable (rows/totals/filters), bukan record ORM.
2. **HTTP controller custom** (`controllers/financial_report.py`, route `type='json'`, `auth='user'`) — 1 route per laporan (`/c18_basic_erp/report/trial_balance`, dst), manggil method di poin 1.
3. **Komponen OWL custom di frontend** (`static/src/report/*.js`, `registry.category("actions").add(...)`) — `useState`, tiap filter berubah langsung `rpc()` ulang lewat `fetchData()` — **live, tanpa tombol Generate, tanpa reload halaman**. Ini beda dari draft awal yang masih mikir pakai `@api.onchange` di wizard Odoo biasa — pola OWL+controller ini lebih ringan & lebih cocok buat kolom dinamis (12-Bulan mode nanti).
4. **Menu**: `ir.actions.client` (`tag` = nama registry action) + `menuitem`, ditaruh di bawah "Accounting > Reports" (`menu_c18_basic_erp_reports_root`, sudah ada dari `c18.fixed.asset.report.wizard`).
5. **Assets**: didaftarkan di `__manifest__.py` key `'assets'` → `web.assets_backend` (JS/XML/SCSS per report) — modul ini sebelumnya tidak punya key `assets` sama sekali, baru ditambah mulai Trial Balance.
6. **Export**: belum diimplementasikan (Excel/PDF, lihat "Belum Diputuskan") — pola referensi `odoo18_toso` sudah nunjukkin caranya (PDF reuse `ir.actions.report`, Excel lewat endpoint `type='http'` terpisah), tinggal diterapkan kalau prioritasnya naik.

### Status Implementasi per Laporan
| Laporan | Status |
|---|---|
| 1. Trial Balance (mode 1-tanggal) | ✅ **Selesai & diverifikasi** — `get_trial_balance_data()`, controller, komponen OWL (`trial_balance_report.js/.xml/.scss`), menu "Reports > Trial Balance". Diverifikasi manual vs 13 transaksi demo, semua angka cocok & balance. |
| 1. Trial Balance (mode 12 Bulan) | ✅ **Selesai & diverifikasi** — `get_trial_balance_yearly_data()` (reuse `_trial_balance_balances()` yang sama dgn mode 1-tanggal, dipanggil 12x), controller, komponen OWL (`trial_balance_yearly_report.js/.xml/.scss`, tabel 24 kolom Debit/Kredit×12 bulan dgn freeze 2 kolom kiri via `position: sticky`), menu "Reports > Trial Balance - 12 Months". Diverifikasi: kolom bulan berjalan (Agustus) cocok persis dgn mode 1-tanggal, bulan tanpa transaksi tampil 0. |
| 2. Buku Besar | ✅ **Selesai & diverifikasi** — `get_general_ledger_data()`, controller, komponen OWL (`general_ledger_report.js/.xml`, termasuk drill-down klik No. Dokumen buka record sumber), menu "Reports > General Ledger". Diverifikasi cross-check ke Trial Balance (saldo akhir akun "Kas" cocok persis di kedua laporan). |
| 3. Neraca (mode 1-tanggal) | ✅ **Selesai & diverifikasi** — `get_balance_sheet_data()`, controller, komponen OWL (`balance_sheet_report.js/.xml`, layout 2 kolom Aset vs Kewajiban+Ekuitas), menu "Reports > Balance Sheet". "Laba Tahun Berjalan" dihitung sesuai aturan timing. Diverifikasi: balance sempurna (Total Aset = Total Kewajiban+Ekuitas) & "Laba Tahun Berjalan" cocok dgn perhitungan manual dari data demo. |
| 3. Neraca (mode 12 Bulan) | ✅ **Selesai & diverifikasi** — `get_balance_sheet_yearly_data()` (reuse `get_balance_sheet_data()` 12x, di-merge per kode akun), controller, komponen OWL (`balance_sheet_yearly_report.js/.xml`, tabel per-section dgn freeze kolom kiri, reuse SCSS dari Trial Balance 12 Bulan). Diverifikasi: semua 12 bulan balance, kolom Agustus cocok persis mode 1-tanggal, "Laba Tahun Berjalan" ikut tampil benar. |
| 4. Laba Rugi (mode 1-rentang) | ✅ **Selesai & diverifikasi** — `get_income_statement_data()`, controller, komponen OWL (`income_statement_report.js/.xml`, struktur berjenjang Pendapatan Bersih→Laba Kotor→Laba Usaha→Laba Bersih), menu "Reports > Income Statement". Diverifikasi cross-check: Laba Bersih cocok persis dgn "Laba Tahun Berjalan" di Neraca. |
| 4. Laba Rugi (mode 12 Bulan) | ✅ **Selesai & diverifikasi** — `get_income_statement_yearly_data()` (reuse `get_income_statement_data()` 12x + 1x rentang setahun penuh utk kolom "Total (YTD)"), controller, komponen OWL (`income_statement_yearly_report.js/.xml`). Diverifikasi: kolom bulan berjalan (Agustus) **dan** kolom Total (YTD) cocok persis dgn mode 1-rentang, bulan tanpa transaksi benar-benar 0 (independen, beda dari Neraca yang kumulatif). |
| 5. Buku Bantu Piutang/Hutang | ✅ **Selesai & diverifikasi** — `get_subsidiary_ledger_data()` (1 method, 2 varian lewat param `ledger_type`), controller, 1 komponen OWL dipakai 2 action registry tag (`subsidiary_ledger_report.js/.xml`), drill-down klik partner buka Buku Besar dgn `account_id`+`partner_id` terisi (General Ledger sekalian ditambah dukungan baca `action.params` awal). Menu "Reports > Subsidiary Ledger - Receivable/Payable". Diverifikasi cocok persis dgn Trial Balance. |
| 6. Laporan Perubahan Ekuitas | ✅ **Selesai & diverifikasi** — `get_equity_changes_data()`, controller, komponen OWL (`equity_changes_report.js/.xml`, matrix 3 kolom Modal/Laba Ditahan/Dividen). Baris "Laba (Rugi) Periode Berjalan" reuse `get_income_statement_data()`. **Keterbatasan diketahui & didokumentasikan**: kalau rentang tanggal melintasi tanggal Tutup Buku, baris Laba Ditahan bisa dobel-hitung (closing entry + baris Laba Periode) - aman untuk kasus umum (periode tidak melintasi Tutup Buku). Diverifikasi: Saldo Akhir Total Ekuitas cocok persis dgn Total Ekuitas Neraca. |

## Aturan Lintas-Laporan (Wajib Diikuti Semua Laporan)

1. **Konversi multi-currency**: semua agregasi debit/kredit **wajib** pakai `debit_company_currency`/`credit_company_currency` (field di `c18.account.move.line`, lihat [01-accounting-foundation.md poin 5](01-accounting-foundation.md#5-multi-currency)) — bukan `debit`/`credit` mentah. Ini pelajaran langsung dari gap yang ditemukan & diperbaiki 2026-08-30 (Tutup Buku/rekonsiliasi Aktiva Tetap sempat salah karena lupa aturan ini).
2. **Exclude jurnal penutup**: baris dari jurnal dengan `is_closing_entry = True` (hasil proses Tutup Buku) **wajib dikecualikan** dari Laba Rugi (supaya akun Pendapatan/Beban yang sudah dinolkan tidak bikin laporan salah nunjukin 0) — field ini memang sudah dibuat khusus buat ini (lihat komentar di `account_move.py`).
3. **Filter Cost Center** (opsional) — semua laporan boleh difilter per `cost_center_id`, konsisten dengan [01 poin 4](01-accounting-foundation.md#4-cost-center-pengganti-account-analytic---c18accountcostcenter). Kosongkan = semua cost center (company-wide).
4. **Hanya baris `state='posted'`** — jurnal draft tidak pernah masuk hitungan laporan manapun.
5. **Drill-down** — tiap baris mutasi (Buku Besar) atau referensi dokumen sumber pakai generic reference (`res_model`/`res_id` di `c18.account.move.line`, [01 poin 3](01-accounting-foundation.md)) buat klik-through ke dokumen aslinya, konsisten dengan pola yang sudah dipakai Kartu Stok.
6. **Trial Balance vs Neraca saling cross-check**: total saldo akun Laba Rugi di Trial Balance (lihat poin 1 di bawah) harus sama persis dengan "Laba Tahun Berjalan" di Neraca (poin 3) pada `date_to` yang sama — kalau beda, ada bug di salah satu implementasinya.

## 1. Trial Balance (Neraca Saldo)

**Tujuan**: snapshot saldo semua akun per tanggal tertentu — alat cek cepat "apa sudah balance" sebelum bikin Neraca/Laba Rugi.

**Filter**: `date_to` (wajib, "per tanggal"), `cost_center_id` (opsional), toggle "Sembunyikan akun bersaldo nol" (default: ON).

**Kolom per baris** (1 baris = 1 akun): Kode Akun, Nama Akun, **Debit** (saldo, cuma keisi kalau akun itu net-debit), **Kredit** (saldo, cuma keisi kalau net-kredit) — bukan 2 kolom "debit total" dan "kredit total" terpisah, tapi 1 saldo bersih ditaruh di kolom sesuai arah normalnya (konvensi standar Trial Balance, sama seperti Accurate/QuickBooks).

**Baris Total** di bawah: total kolom Debit = total kolom Kredit (kalau tidak sama, ada bug di sistem — laporan ini fungsinya justru buat mendeteksi itu, jadi mismatch harus **ditampilkan mencolok**, bukan disembunyikan).

**Perhitungan — beda basis window tanggal tergantung sifat akun** (dibahas & dikonfirmasi 2026-08-30, poin krusial yang gampang salah kalau tidak eksplisit):

- **Akun Neraca** (`account_type` masuk kategori Aset/Kewajiban/Ekuitas — lihat daftar tipe di poin 3 di bawah) — sifatnya **permanen**, saldo terus terbawa sejak awal, tidak pernah di-nol-kan. Window: `date <= date_to` (tanpa batas bawah).
- **Akun Laba Rugi** (`revenue`, `cost_of_revenue`, `expense`, `other_revenue`, `other_expense`) — sifatnya **sementara (nominal account)**, di-nol-kan tiap tahun lewat Tutup Buku. Saldonya cuma bermakna **dalam 1 tahun fiskal berjalan**. Window: `date >= 1 Januari tahun date_to` **dan** `date <= date_to` — **akumulasi sejak awal tahun, BUKAN cuma hari/bulan itu saja**. Alasan: supaya konsisten dengan cara hitung "Laba Tahun Berjalan" di Neraca (poin 3 di bawah) — total saldo semua akun Laba Rugi di Trial Balance **harus sama persis** dengan angka "Laba Tahun Berjalan" yang tampil di Neraca pada `date_to` yang sama (2 laporan saling mengkonfirmasi, bisa dipakai cross-check). Kalau window-nya beda (mis. cuma harian/bulanan), 2 laporan ini jadi tidak nyambung tanpa alasan yang benar.
  - **Tidak perlu exclude `is_closing_entry` secara eksplisit di sini** (beda dari aturan Laba Rugi poin 4) — karena window selalu dimulai dari 1 Jan tahun `date_to`, jurnal penutup dari tahun-tahun SEBELUMNYA otomatis jatuh di luar window. Satu-satunya jurnal penutup yang bisa masuk window adalah milik tahun `date_to` itu sendiri (kalau `date_to = 31 Des` dan Tutup Buku tahun itu sudah posted) — dan itu memang **seharusnya** ikut terhitung (saldo Laba Rugi jadi 0, sudah pindah ke Laba Ditahan), sama seperti aturan Neraca poin 3.

`saldo akun = SUM(debit_company_currency) - SUM(credit_company_currency)` untuk `c18.account.move.line` dengan `account_id` itu, `state='posted'`, window tanggal sesuai kategori di atas (+ filter cost center kalau diisi). Kalau hasil positif → taruh di kolom Debit; negatif → taruh di kolom Kredit (nilai absolut).

### Mode Tampilan "12 Bulan" (ditambah 2026-08-30, ternyata memungkinkan — dicek ulang setelah sempat ditulis "kurang relevan")

**Sama persis mekanismenya dengan mode 12 Bulan Neraca** (bukan kebetulan — Trial Balance itu sifatnya point-in-time juga, dan aturan window ganda di atas sudah otomatis kompatibel): tinggal ulang rumus yang sama per akhir bulan, `date_to` beda tiap kolom (akun Neraca tetap kumulatif sejak awal per kolom; akun Laba Rugi tetap kumulatif sejak 1 Jan tahun itu sampai akhir bulan kolom itu — bukan cuma bulan itu sendiri, sama seperti aturan "Laba Tahun Berjalan").

**Filter mode ini**: `year` — menggantikan `date_to` tunggal.

**Kolom**: tiap bulan (Jan-Des) jadi **sepasang** kolom Debit/Kredit (bukan 1 kolom net) — supaya validasi "Total Debit = Total Kredit" (fungsi inti Trial Balance) tetap bisa dicek **per bulan**, bukan cuma di kolom terakhir. Ini bikin tabelnya lebar (12 bulan × 2 = 24 kolom + Kode/Nama Akun) — presentasinya mirip **"Kertas Kerja"/"Neraca Lajur"** (worksheet akuntansi tradisional Indonesia yang memang berbentuk begini), bukan sesuatu yang aneh untuk laporan jenis ini.

**Ilustrasi ringkas** (angka contoh, dipotong 2 bulan biar muat — implementasi asli tetap 12 bulan):

| Akun | Jan (D) | Jan (K) | Feb (D) | Feb (K) | ... |
|---|---:|---:|---:|---:|---|
| 1-1000 Kas | 45.000.000 | – | 48.000.000 | – | ... |
| 2-1000 Hutang Usaha | – | 20.000.000 | – | 18.500.000 | ... |
| 4-1000 Pendapatan Penjualan/Jasa | – | 11.000.000 | – | 23.500.000 | ... |
| **Total** | **...** | **...** | **...** | **...** | ... |

Baris "4-1000 Pendapatan" di kolom Feb (23.500.000) itu **akumulasi Jan+Feb**, bukan Feb saja — sesuai aturan window akun Laba Rugi di atas. Beda karakter dari mode 12 Bulan Laba Rugi (poin 4) yang independen per bulan — dua laporan ini punya window berbeda **secara sengaja** walau sama-sama nampilin akun Laba Rugi, jangan disamakan logic-nya.

## 2. Buku Besar (General Ledger) per Akun

**Tujuan**: mutasi kronologis 1 akun spesifik — buat audit/telusur kenapa saldo akun itu jadi sekian. Pola identik Kartu Stok ("1 laporan = 1 akun"), bukan kebetulan — memang didesain simetris.

**Filter**: `account_id` (wajib), `date_from`/`date_to`, `cost_center_id` (opsional), **`partner_id`** (opsional, ditambah 2026-08-30 — dipakai buat drill-down dari Buku Bantu Piutang/Hutang di poin 5, tapi juga berguna sendiri buat lihat histori transaksi 1 partner di akun manapun).

**Baris "Saldo Awal"** (sebelum `date_from`, bukan mutasi): `SUM(debit_company_currency) - SUM(credit_company_currency)` untuk semua baris `date < date_from`.

**Kolom per baris mutasi** (urut kronologis by `date` + `id`, 1 baris = 1 `c18.account.move.line`): Tanggal, No. Dokumen (dari `move_id.name`, drill-down ke sumber via `res_model`/`res_id` kalau ada — kalau kosong berarti jurnal manual, drill-down ke `c18.account.move` itu sendiri), Keterangan (`name` di line, fallback `move_id.ref`), Partner (opsional, kalau ada), Debit, Kredit, **Saldo Berjalan** (running balance kumulatif dari Saldo Awal, nambah kalau searah normal balance akun/berkurang kalau lawan arah — sama logic kayak kolom Trial Balance tapi kumulatif per baris, bukan cuma titik akhir).

**Baris Total** di bawah: total Debit periode, total Kredit periode, **Saldo Akhir** (= Saldo Awal + Debit periode − Kredit periode, harus sama persis dengan baris terakhir kolom Saldo Berjalan).

## 3. Neraca (Balance Sheet)

**Tujuan**: posisi keuangan per tanggal tertentu (point-in-time), dikelompokkan Aset/Kewajiban/Ekuitas.

**Filter**: `date_to` (wajib), `cost_center_id` (opsional — walau Neraca biasanya company-wide, tetap didukung sebagai turunan sesuai [06 poin 3](06-accounting-business.md#3-laporan-keuangan-tier-standard)).

**Struktur** (grouped by `account_type`, urutan tetap sesuai kode akun poin 1-9 di CoA):
- **ASET**: `cash_bank`, `receivable`, `inventory`, `other_current_asset` → subtotal "Total Aset Lancar". Lalu `fixed_asset` (**tampilkan gross value + baris "Akumulasi Penyusutan" sebagai pengurang eksplisit**, walau sama-sama `account_type=fixed_asset` — bukan digabung jadi 1 angka, presentasi Neraca standar selalu pisah gross vs akumulasi), `other_asset` → subtotal "Total Aset Tidak Lancar". Jumlah keduanya = **Total Aset**.
- **KEWAJIBAN**: `payable`, `other_current_liability` → subtotal "Total Kewajiban Lancar". `long_term_liability` → subtotal "Total Kewajiban Jangka Panjang". Jumlah keduanya = **Total Kewajiban**.
- **EKUITAS**: akun `equity` biasa (Modal, dst) **ditambah** baris khusus **"Laba Tahun Berjalan"** (lihat aturan timing di bawah) = **Total Ekuitas**.
- **Validasi**: Total Aset **harus** = Total Kewajiban + Total Ekuitas — kalau tidak, tampilkan warning mencolok (indikasi bug, sama prinsipnya dengan Trial Balance).

**Aturan "Laba Tahun Berjalan" (SUDAH ditulis di [06 poin C](06-accounting-business.md#c-tutup-buku--belum-ada-requirement-sama-sekali-sebelum-ini-scope-baru-diriset-dari-pola-accurate-online-konsisten-dengan-misi-lebih-mirip-odoo18_accurate) baris 66-68, dikutip ulang di sini karena krusial buat implementasi Neraca)**:
- Kalau `date_to` **belum melewati** tanggal Tutup Buku tahun fiskal yang mencakup `date_to` (atau tahun itu belum pernah ditutup sama sekali) → hitung **on-the-fly**: `SUM(revenue+other_revenue) - SUM(cost_of_revenue+expense+other_expense)` untuk `date` dari 1 Jan tahun itu sampai `date_to`, exclude `is_closing_entry` (walau seharusnya belum ada closing entry di tahun berjalan). Tampilkan sebagai baris **terpisah** "Laba Tahun Berjalan" di Ekuitas.
- Kalau `date_to >= 31 Des` tahun itu **dan** Tutup Buku tahun itu **sudah posted** → jangan hitung ulang, karena sudah otomatis masuk ke saldo akun **"3-1100 Laba Ditahan"** lewat jurnal penutup — baris "Laba Tahun Berjalan" terpisah **tidak muncul** (mencegah double count).

### Mode Tampilan "12 Bulan" (ditambah 2026-08-30, diminta user)

Selain mode "1 tanggal" di atas, Neraca juga punya mode tampilan **12 kolom** (Jan-Des) — bukan laporan terpisah, cuma cara lain nampilin data yang sama.

**Filter mode ini**: `year` (tahun fiskal) — **menggantikan** `date_to` tunggal saat mode ini aktif.

**Kolom**: Jan, Feb, ..., Des — tiap kolom = snapshot Neraca per **akhir bulan itu** (`date_to` = tanggal terakhir bulan tsb), dihitung **independen** pakai rumus persis sama seperti mode 1-tanggal di atas (cuma `date_to` beda tiap kolom). Baris (Aset/Kewajiban/Ekuitas + subtotal) **sama persis** dengan mode 1-tanggal.

**"Laba Tahun Berjalan" per kolom**: tetap ikut aturan timing di atas, tapi **akumulatif dari 1 Jan tahun itu sampai akhir bulan kolom itu** (bukan cuma bulan itu sendiri) — konsisten sifat Neraca yang point-in-time. Jadi kolom Maret = akumulasi Jan-Mar, kolom Desember = akumulasi Jan-Des (atau 0 kalau Tutup Buku tahun itu sudah posted per 31 Des).

**Ilustrasi ringkas** (angka contoh, dipotong cuma 4 kolom biar muat — implementasi asli tetap 12 kolom Jan-Des):

| Akun | Jan | Feb | Mar | ... | Des |
|---|---:|---:|---:|---|---:|
| Kas | 45.000.000 | 48.000.000 | 52.000.000 | ... | 70.000.000 |
| Bank | 120.000.000 | 115.000.000 | 130.000.000 | ... | 180.000.000 |
| ... | | | | | |
| **Total Aset** | **...** | **...** | **...** | ... | **...** |
| ... | | | | | |
| Laba Tahun Berjalan | 5.000.000 | 9.500.000 | 15.200.000 | ... | 31.500.000 |
| **Total Ekuitas** | **...** | **...** | **...** | ... | **...** |

## 4. Laba Rugi (Profit & Loss / Income Statement)

**Tujuan**: kinerja operasional selama 1 rentang periode (bukan point-in-time seperti Neraca).

**Filter**: `date_from`/`date_to` (wajib, rentang — lazimnya 1 bulan atau 1 tahun berjalan), `cost_center_id` (opsional, ini yang paling sering dipakai buat P&L per departemen/project).

**Struktur berjenjang** (grouped by `account_type`, tiap baris subtotal berlabel jelas):
1. **Pendapatan** (`revenue`, termasuk akun kontra-revenue "Retur & Potongan Penjualan" sebagai **pengurang**, bukan baris terpisah negatif) → **Pendapatan Bersih**.
2. Dikurangi **Beban Pokok Pendapatan** (`cost_of_revenue`) → **Laba Kotor**.
3. Dikurangi **Beban Usaha** (`expense`) → **Laba Usaha (Operating Income)**.
4. Ditambah **Pendapatan Lain-lain** (`other_revenue`), dikurangi **Beban Lain-lain** (`other_expense`) → **Laba Bersih (Net Income)** — angka ini yang jadi "Laba Tahun Berjalan" di Neraca kalau `date_from`/`date_to` laporan ini disamakan dengan awal tahun fiskal s/d tanggal Neraca.

**Wajib exclude `is_closing_entry=True`** (aturan lintas-laporan poin 2 di atas) — ini yang paling kritis di laporan ini spesifik, karena kalau kelewat, jurnal penutup Tutup Buku bakal nolkan Pendapatan/Beban yang sedang dihitung dan laporan salah nunjukin 0 untuk periode yang justru mau dilihat.

**Ilustrasi** (angka contoh, bukan data nyata — nunjukkin format berjenjang & indentasi per level subtotal):

| Akun | Nominal |
|---|---:|
| Pendapatan Penjualan/Jasa | 150.000.000 |
| (–) Retur & Potongan Penjualan | (2.000.000) |
| **Pendapatan Bersih** | **148.000.000** |
| (–) Beban Pokok Pendapatan/HPP | (90.000.000) |
| **Laba Kotor** | **58.000.000** |
| Beban Usaha: | |
| &nbsp;&nbsp;Beban Gaji | 12.000.000 |
| &nbsp;&nbsp;Beban Sewa | 10.000.000 |
| &nbsp;&nbsp;Beban Operasional | 3.000.000 |
| &nbsp;&nbsp;Beban Penyusutan | 1.500.000 |
| &nbsp;&nbsp;Beban ATK | 500.000 |
| (–) Total Beban Usaha | (27.000.000) |
| **Laba Usaha (Operating Income)** | **31.000.000** |
| (+) Pendapatan Lain-lain | 800.000 |
| (–) Beban Lain-lain | (300.000) |
| **Laba Bersih (Net Income)** | **31.500.000** |

Catatan baca tabel: baris akun individual (Beban Gaji, Beban Sewa, dst) muncul apa adanya sesuai akun yang benar-benar punya transaksi di periode itu (bukan daftar fixed — akun yang saldonya 0 di periode itu tidak perlu muncul). Baris **bold** adalah subtotal/total berjenjang sesuai poin 1-4 di atas, bukan akun individual.

### Mode Tampilan "12 Bulan" (ditambah 2026-08-30, diminta user)

Sama seperti Neraca, Laba Rugi juga punya mode **12 kolom** (Jan-Des) — cuma beda sifat: karena Laba Rugi itu laporan **per rentang** (bukan point-in-time), tiap kolom bulan dihitung **independen** (BUKAN akumulatif kayak Neraca) — kolom Maret cuma isi transaksi tanggal 1-31 Maret saja, tidak termasuk Jan-Feb.

**Filter mode ini**: `year` (tahun fiskal) — menggantikan `date_from`/`date_to` custom saat mode ini aktif.

**Kolom**: Jan, Feb, ..., Des, **+ 1 kolom terakhir "Total (YTD)"** — total akumulasi 1 tahun penuh, setara laporan 1-periode dengan `date_from` = 1 Jan, `date_to` = 31 Des tahun itu (juga setara menjumlah 12 kolom bulanan — harus sama persis, cross-check tambahan). Baris (struktur berjenjang Pendapatan Bersih → Laba Kotor → Laba Usaha → Laba Bersih) **sama persis** dengan mode 1-periode. Aturan **wajib exclude `is_closing_entry`** tetap berlaku di semua kolom termasuk Total (YTD).

**Ilustrasi ringkas** (angka contoh, dipotong 4 kolom + Total — implementasi asli tetap 12 kolom Jan-Des + Total):

| Akun | Jan | Feb | Mar | ... | Des | **Total (YTD)** |
|---|---:|---:|---:|---|---:|---:|
| Pendapatan Penjualan/Jasa | 11.000.000 | 12.500.000 | 13.000.000 | ... | 15.000.000 | **150.000.000** |
| (–) Retur & Potongan Penjualan | (200.000) | – | (300.000) | ... | – | **(2.000.000)** |
| **Pendapatan Bersih** | **10.800.000** | **12.500.000** | **12.700.000** | ... | **15.000.000** | **148.000.000** |
| (–) Beban Pokok Pendapatan/HPP | (6.500.000) | (7.200.000) | (7.800.000) | ... | (9.500.000) | **(90.000.000)** |
| **Laba Kotor** | **4.300.000** | **5.300.000** | **4.900.000** | ... | **5.500.000** | **58.000.000** |
| ... | | | | | | |
| **Laba Bersih (Net Income)** | **2.100.000** | **2.400.000** | **2.550.000** | ... | **2.600.000** | **31.500.000** |

## 5. Buku Bantu Piutang / Buku Bantu Hutang (Subsidiary Ledger)

Ditambah 2026-08-30 (gap ditemukan user saat review — sebelumnya cuma "4 laporan dikonfirmasi" per keputusan 2026-08-26 di [06 poin 3](06-accounting-business.md#3-laporan-keuangan-tier-standard), Buku Bantu belum kepikiran). **2 laporan terpisah, struktur identik** — Buku Bantu Piutang (breakdown akun "1-1200 Piutang Usaha" per customer) dan Buku Bantu Hutang (breakdown akun "2-1000 Hutang Usaha" per vendor).

**Tujuan**: Buku Besar akun "Piutang Usaha"/"Hutang Usaha" cuma nunjukkin total gabungan SEMUA partner — tidak kelihatan siapa berhutang/dihutangi berapa. Buku Bantu memecah saldo itu **per partner**.

**Filter**: `date_to` (wajib), toggle "Sembunyikan partner bersaldo nol" (default ON).

**Kolom per baris** (1 baris = 1 partner yang punya transaksi di akun kontrol itu): Nama Partner, Saldo (1 kolom nilai — arahnya sudah pasti per jenis laporan: Piutang selalu debit-normal, Hutang selalu credit-normal, jadi tidak perlu 2 kolom Debit/Kredit terpisah kayak Trial Balance).

**Perhitungan**: `saldo per partner = SUM(debit_company_currency) - SUM(credit_company_currency)` (Piutang) atau kebalikannya `credit - debit` (Hutang, supaya tampil positif) untuk `c18.account.move.line` dengan `account_id` = akun kontrol (`c18_basic_erp.acc_1_1200` / `c18_basic_erp.acc_2_1000`), `partner_id` = partner itu, `state='posted'`, `date <= date_to`.

**Baris Total** — wajib sama persis dengan saldo akun "Piutang Usaha"/"Hutang Usaha" itu sendiri di Trial Balance/Buku Besar pada `date_to` yang sama (cross-check lagi, pola sama seperti aturan lintas-laporan poin 6).

**Drill-down**: klik nama partner → buka **Buku Besar** (poin 2) dengan `account_id` + `partner_id` otomatis terisi (makanya poin 2 ditambah filter `partner_id` opsional).

## 6. Laporan Perubahan Ekuitas (Statement of Changes in Equity) — sesuai PSAK 1

Ditambah 2026-08-30 (diminta user, diriset formatnya). PSAK 1 mewajibkan laporan ini sebagai salah satu dari 5 laporan keuangan pokok — sebelumnya tidak masuk daftar "4 laporan dikonfirmasi" 2026-08-26, murni kelewat, bukan sengaja ditunda.

**Riset format** (cross-check beberapa sumber — Mekari Jurnal, Bee.id, ringkasan PSAK 1/IAS 1): format standarnya **matrix** — kolom = tiap komponen ekuitas, baris = jenis pergerakan periode (Saldo Awal → pergerakan-pergerakan → Saldo Akhir), direkonsiliasi terpisah per kolom. PSAK 1 penuh (PT Tbk) bisa punya banyak kolom (saham biasa, agio saham, cadangan, dst) — **modul ini pakai versi ringkas** sesuai skala UKM (konsisten misi proyek "lebih mirip Accurate/pembukuan UKM"), cukup 3 kolom sesuai akun ekuitas yang sudah ada di CoA: **Modal** (3-1000), **Laba Ditahan** (3-1100), **Dividen** (3-1300).

**Tujuan**: rekonsiliasi saldo tiap komponen ekuitas dari awal ke akhir periode — komponen apa berubah karena apa (laba/rugi periode berjalan, setoran/penarikan modal, dividen/prive).

**Filter**: `date_from`/`date_to` (rentang periode, lazimnya 1 tahun fiskal). **Tidak ada filter `cost_center_id`** — beda dari laporan lain, ekuitas selalu company-wide, tidak masuk akal dipecah per cost center.

**Struktur** (baris × kolom):

| Baris \\ Kolom | Modal (3-1000) | Laba Ditahan (3-1100) | Dividen (3-1300) | Total Ekuitas |
|---|---|---|---|---|
| Saldo Awal (per `date_from`) | ... | ... | ... | ... |
| Setoran/Penarikan Modal | ... | – | – | ... |
| Laba (Rugi) Periode Berjalan | – | ... | – | ... |
| Dividen/Prive Diumumkan | – | – | ... | ... |
| **Saldo Akhir** (per `date_to`) | **...** | **...** | **...** | **...** |

**Perhitungan tiap baris**:
- **Saldo Awal**: saldo akun itu per `date_from` — akumulasi sejak awal (`date < date_from`), karena Modal/Laba Ditahan/Dividen itu akun Neraca permanen (aturan window sama seperti Trial Balance poin 1).
- **Setoran/Penarikan Modal**: `SUM(credit_company_currency) - SUM(debit_company_currency)` akun "3-1000 Modal", HANYA baris dengan `date` di rentang `[date_from, date_to]` (net pergerakan periode itu saja, BUKAN kumulatif sejak awal — beda dari baris Saldo Awal).
- **Laba (Rugi) Periode Berjalan**: **reuse angka yang sama persis** dari "Laba Bersih (Net Income)" di Laporan Laba Rugi (poin 4) untuk rentang `date_from`-`date_to` yang sama — jangan hitung ulang pakai rumus terpisah, supaya tidak ada 2 sumber kebenaran buat 1 angka yang sama.
- **Dividen/Prive**: net pergerakan akun "3-1300 Dividen" periode itu (pola sama seperti baris Setoran Modal).
- **Saldo Akhir**: Saldo Awal + semua baris pergerakan di atas untuk kolom yang sama — **wajib sama persis** dengan saldo akun itu di Trial Balance/Neraca pada `date_to` (cross-check lagi, pola sama seperti aturan lintas-laporan poin 6).

**Catatan akun "3-1900 Balancing Account"**: ini akun plug/system (buat nge-balance data transisi/impor, bukan komponen ekuitas riil pemilik) — **dikecualikan** dari matrix ini. Kalau saldonya tidak 0, itu indikasi bug/data tidak balance di tempat lain, bukan sesuatu yang wajar ditampilkan di sini.

## Belum Diputuskan (Perlu Digali Saat Implementasi)
- Format export (PDF/Excel) — belum dibahas sama sekali, kemungkinan cukup tampilan `list` view dulu (konsisten pola laporan lain di modul ini yang belum ada export khusus).

## Ditunda (Sengaja)
- Perbandingan bebas 2 periode custom pilihan user (mis. "Q1 2025 vs Q1 2026" atau "tahun ini vs tahun lalu berdampingan") — **dikonfirmasi tidak perlu dulu** (2026-08-30), beda dari mode "12 Bulan" (poin 1/3/4) yang tetap masuk scope. Bisa direvisit kalau nanti dibutuhkan.
