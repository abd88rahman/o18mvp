# Titik Akhir Sesi Ini (2026-08-30)

## Kalimat Penutup Sesi
> (menunggu instruksi lanjutan dari user — sesi ini sangat panjang: setup infra (nginx), bugfix akuntansi (multi-currency, validasi Kas Bank), full translation UI ke Inggris, Laporan Keuangan + Kartu Stok, sistem pencatatan Persediaan Perpetual/Periodik, lalu ditutup dengan eksekusi penuh skenario testing PT Roda Sejahtera di 4 tema Perpetual/Periodik×FIFO/Average (semua LABA), perapian dokumen testing, drill-down jurnal di 18 form, dan housekeeping database jadi cuma 4 tersisa. Tidak ada pertanyaan terbuka spesifik di akhir, murni permintaan "update" catatan sesi.)

## Ringkasan Progres Sesi Ini

### 1. Setup Nginx + SSL Production (`sub1.domain.id`)
Server cloud sudah punya nginx + certbot terpasang untuk `sub1.domain.id` (odoo1, repo ini), lengkap dengan SSL. Ketemu & diperbaiki 2 kendala saat setup: error `socket() [::]:80` (IPv6 tidak didukung server, solusi hapus `sites-enabled/default`) dan nginx belum pernah di-`start` (bukan reload). Panduan lengkap + kendala ini dicatat di [`setting-nginx-multi-domain-ssl.md`](setting-nginx-multi-domain-ssl.md). `sub2.domain.id` (odoo2, repo lain) masih rencana — belum ada repo/container-nya.

### 2. Gap Multi-Currency — DITEMUKAN & DIPERBAIKI (selesai penuh)
- ERD ([01-accounting-foundation.md poin 5](../../erd/mvp/01-accounting-foundation.md#5-multi-currency)) diperjelas dulu sebelum ubah kode — sebelumnya tidak eksplisit soal aturan konversi saat agregasi lintas jurnal.
- Kode: tambah computed stored field `debit_company_currency`/`credit_company_currency` di `c18.account.move.line` (`account_move.py`), dipakai di titik agregasi yang tadinya salah jumlah nilai mentah lintas currency: Tutup Buku (`account_closing.py`), rekonsiliasi & laporan Aktiva Tetap (`fixed_asset.py`, `fixed_asset_report.py`). Bug tambahan ikut diperbaiki: `c18.fixed.asset.entry` sebelumnya tidak punya field `exchange_rate` sendiri (selalu default kurs 1.0 walau `currency_id` beda).
- **Diverifikasi** via `odoo shell` (skenario cross-currency, company currency vs currency asing beda) — hasil konversi & agregasi benar. Status di [`erd/mvp/00-status-requirement.md`](../../erd/mvp/00-status-requirement.md) sudah diupdate mencerminkan ini "selesai", bukan lagi gap terbuka.

### 3. Fix Validasi Kas Bank
- Transfer: `account_id_dest` tidak boleh sama dengan `account_id` asal (domain view + `UserError` di `action_post`).
- Kas Masuk/Keluar: akun lawan (`line_ids.account_id`) tidak boleh bertipe Kas/Bank — harus pakai Transfer untuk kas-ke-kas (domain view + `UserError`).
- ERD [06-accounting-business.md poin B](../../erd/mvp/06-accounting-business.md#L49) diupdate menegaskan aturan ini.

### 4. Konsistensi Kecil Lain
- `account_move.py`: field `name` (Jurnal Umum) disamakan ke pola `'New'` → `draft-<id>` yang dipakai 22 model lain (sebelumnya unik pakai `'/'`).
- `amount_total` (Jurnal Umum, cuma sisi debit) diganti jadi `total_debit` + `total_credit` terpisah — lebih informatif terutama pas draft/belum balance.

### 5. Full Translation UI `c18_basic_erp` ke Inggris + Rename Kode Teknis
Keputusan besar user: seluruh UI modul (`app/mvp/c18_basic_erp/`) dialihkan dari Bahasa Indonesia ke Inggris — bukan cuma 1 field, tapi label field, judul menu/action, label opsi Selection, pesan error, help text. Dikerjakan lewat background agent (50 file: 29 model + 21 view), terverifikasi `py_compile` + XML valid.

**Susulan (ditemukan user sendiri saat review)**: kode teknis `account_type` (bukan cuma label-nya) juga di-rename ke Inggris — `kas_bank`→`cash_bank`, `piutang_usaha`→`receivable`, `hutang_usaha`→`payable`, `persediaan`→`inventory`, `aktiva_tetap`→`fixed_asset`, dst (15 kode total). Disinkronkan ke SEMUA referensi: domain di views, filter Python (`account_cash.py`, `fixed_asset.py`, `payroll.py`, dll), `PL_ACCOUNT_TYPES` di `account_closing.py`, dan **42 record CoA** di `data/account_account_data.xml`.

**Dikecualikan dari translasi** (keputusan eksplisit): nama akun CoA & nama Journal di data master (tetap Indonesia, dianggap konten akuntansi bukan UI chrome), komentar kode, `__manifest__.py`, dan folder `erd/`/`notes/`/`testing/`.

**Diverifikasi menyeluruh**: install bersih modul ke database baru + smoke test fungsional (Kas Masuk, Transfer, Fixed Asset+rekonsiliasi, Tutup Buku, 2 validasi error) — semua PASS dengan kode & pesan baru.

### 6. Database Lokal
- **`o18mvp` dan `test_c18_basic_erp` DIHAPUS** (permintaan eksplisit user) — database kerja lokal Docker lama sudah tidak ada lagi.
- **`test-01` dibuat baru** — `base`+`c18_theme`+`c18_basic_erp` terinstall, login `admin`/`admin`, currency **IDR**, country **Indonesia** (default awal sempat USD karena CLI tidak set Country, sudah dikoreksi).
- Prosedur baku bikin database baru (beda dari alur Database Manager UI biasa: master password, admin login, country, demo data masing-masing jadi langkah terpisah) didokumentasikan di [`cara-buat-database-baru.md`](cara-buat-database-baru.md).

### 7. Skenario Testing "PT Roda Sejahtera" — Tutup Buku 2025 Ditunda
Atas permintaan user, urutan skenario diubah: Tutup Buku Fiscal Year 2025 **tidak** langsung diproses di akhir Des 2025 (beda dari pola Tutup Buku 2024), tapi ditunda sampai setelah transaksi Feb 2026 — supaya bisa diamati saldo akun "3-1100 Laba Ditahan" **sebelum** vs **sesudah** Tutup Buku 2025 diproses. 3 dokumen diupdate: [`00-skenario-distributor-ban.md`](../../testing/mvp/00-skenario-distributor-ban.md), [`01-transaksi-distributor-ban.md`](../../testing/mvp/01-transaksi-distributor-ban.md) (2 checkpoint baru ditambah), [`02-prosedur-testing.md`](../../testing/mvp/02-prosedur-testing.md).

### 8b. Susulan Setelah Update Awal — TODO 6 & TODO 10 Selesai
- **Sync `.rst` di `c18_help`** (TODO 6 lama): terbukti out-of-sync (masih teks lama "Tutup Buku 2025 proses sekarang"). Diregenerasi dari `.md` sumber pakai `pandoc` (bukan edit manual), dibersihkan dari 13 dead-link (link markdown antar-dokumen yang jadi hyperlink RST menuju file tidak ada di konteks Odoo). Diverifikasi 2 lapis: parse `docutils` langsung + `_render_rst()` sungguhan lewat `odoo shell` di `test-01` — semua PASS.
- **Database kerja** (TODO 10 lama): diputuskan **`test-01` dipakai sebagai database kerja**, tidak perlu bikin database baru lagi.

### 8. Diskusi Dokumentasi & Demo Data
- Klarifikasi konsep 3 jenis "data" yang sering tertukar: **Demo Data** (mekanisme Odoo, `c18_basic_erp` belum punya sama sekali), **Test Plan/UAT Script** (isi `testing/mvp/`, dijalankan manual), **Default/Config Data** (CoA/Journal/Sequence, auto-load selalu).
- Rencana ke depan (belum dikerjakan): kalau nanti ada User Guide untuk client, harus dipisah dari QA/Testing guide (`c18_help`) — beda audiens, beda konten. Folder [`docs/user-guide/`](../../docs/user-guide/) sudah di-scaffold (baru README, isi kosong) sebagai tempatnya nanti.

### 9. `c18_help` Resmi Jadi Permanen (TODO 8 lama, selesai)
Keputusan: `c18_help` **permanen**, tapi scope-nya cuma internal tester/QA (bukan client) — lihat diskusi TODO 5 (lama)/8 di atas. Dieksekusi: label menu "Help" → **"QA Guide"** (+komentar penjelasan di `menu.xml`), manifest keluar dari status prototype (nama modul "ERP QA Guide", deskripsi menegaskan internal-only + larangan install ke database demo/client), PRD baru ditulis di [`erd/base/06-qa-guide-viewer.md`](../../erd/base/06-qa-guide-viewer.md) (latar belakang, tabel keputusan desain, cara kerja teknis, **prosedur sinkronisasi `.rst`** biar tidak terulang out-of-sync). `erd/base/00-status-requirement.md` diupdate. Disinkronkan ke `test-01` (`-u c18_help` + restart), terverifikasi menu berubah jadi "QA Guide" di database.

### 10. Demo Data untuk Presentasi Client Selesai (TODO 5 lama, selesai)
Dibangun `c18.basic.erp.demo.generator` (`models/demo_generator.py`, Python bukan XML statis — karena tiap transaksi butuh `action_post()` supaya jurnal beneran ter-generate) — ~13 dokumen contoh (Kas Masuk/Keluar/Transfer, siklus Pembelian penuh, siklus Penjualan penuh, Aktiva Tetap, Payroll), tanggal relatif ke hari generate, Tutup Buku sengaja di-skip.

**Kendala teknis nyata ditemukan**: rencana awal pakai mekanisme `'demo'` bawaan Odoo (centang "Demo Data" saat create db) **tidak bisa dipakai** — dibuktikan 2x test + cross-check ke source Odoo (`odoo/modules/graph.py`, `odoo/tools/config.py`): modul `auto_install: True` (seperti `c18_basic_erp`, wajib tetap begitu) **tidak pernah kebagian flag demo**, apa pun cara installnya. Dipivot ke trigger manual (`env['c18.basic.erp.demo.generator']._generate()` lewat `odoo shell`, idempotent lewat `ir.config_parameter` guard).

**Bug ditemukan & diperbaiki saat testing**: generator awal pakai `c18.payroll.accrual.action_pay()` yang tidak mengisi `account_id` wajib di Payroll Payment (NotNullViolation) — diperbaiki jadi `create()` manual langsung isi `account_id`.

### 11. Laporan Keuangan + Kartu Stok — TODO 2 SEKARANG 100% SELESAI (progres paling besar sesi ini)
Kartu Stok requirement-nya sudah lengkap dari sesi sebelumnya. Requirement 7 laporan baru ditulis sesi ini di dokumen baru [`erd/mvp/09-laporan-keuangan.md`](../../erd/mvp/09-laporan-keuangan.md) (awalnya 4, diperluas beberapa kali: +Buku Bantu Piutang/Hutang, +Laporan Perubahan Ekuitas sesuai PSAK 1 — diriset via WebSearch, +mode tampilan "12 Bulan" untuk Trial Balance/Neraca/Laba Rugi).

**Poin krusial yang dibahas & diperjelas user soal Trial Balance**: menampilkan SEMUA akun dalam 1 tanggal (`date_to`), tapi akun Neraca (permanen) vs akun Laba Rugi (nominal, di-nol-kan tiap tahun) butuh **window tanggal beda** — Neraca: `date <= date_to` tanpa batas bawah; Laba Rugi: akumulasi **dari 1 Januari tahun `date_to`** (bukan cuma harian/bulanan) supaya konsisten dengan "Laba Tahun Berjalan" di Neraca (2 laporan saling cross-check, totalnya harus sama persis).

**Pivot arsitektur implementasi besar**: rencana awal wizard `TransientModel` + tombol "Generate" (pola `fixed_asset_report.py` yang sudah ada) diganti total setelah user tunjuk contoh report slip gaji interaktif di repo referensi **`d:\Odoo Dev\odoo18_toso`** (`c18_hr_payroll`). Pola yang diadopsi: **`models.AbstractModel`** (logic murni, tanpa tabel) + **HTTP controller custom** (`type='json'`) + **komponen OWL** (`registry.category("actions")`, `useState`, live `rpc()` tiap filter berubah — tanpa tombol Generate/reload). Detail lengkap arsitektur ada di `erd/mvp/09-laporan-keuangan.md` bagian "Arsitektur Implementasi".

**SEMUA 9 laporan/mode SELESAI & DIVERIFIKASI** (sesi ini tuntas penuh, tidak ada sisa kecuali export PDF/Excel opsional):
1. Trial Balance (1-tanggal & **12-Bulan**) — `get_trial_balance_data()`/`get_trial_balance_yearly_data()`.
2. Buku Besar — `get_general_ledger_data()`, drill-down klik No. Dokumen.
3. Neraca (1-tanggal & **12-Bulan**) — `get_balance_sheet_data()`/`get_balance_sheet_yearly_data()`, hitung "Laba Tahun Berjalan" sesuai aturan timing.
4. Laba Rugi (1-rentang & **12-Bulan** + kolom "Total (YTD)") — `get_income_statement_data()`/`get_income_statement_yearly_data()`, exclude `is_closing_entry`.
5. Buku Bantu Piutang & Hutang — `get_subsidiary_ledger_data()` (1 method, 2 varian), drill-down ke Buku Besar dgn `account_id`+`partner_id` terisi.
6. Laporan Perubahan Ekuitas — `get_equity_changes_data()`, reuse angka Laba Bersih dari poin 4 (1 sumber kebenaran, bukan hitung ulang).

### 11b. Kartu Stok + Saldo Persediaan — SELESAI, tapi BUTUH UBAH MESIN COSTING DULU (temuan besar tak terduga)
Saat mendesain Kartu Stok, ketemu 2 gap struktural nyata di mesin costing yang sudah ada (bukan cuma soal bikin laporan baru):

1. **FIFO**: `c18.stock.layer` cuma nyimpan STATE SAAT INI (qty sisa per layer), bukan histori per-transaksi — jadi kebutuhan requirement "split baris keluar per layer kalau melewati batas antar-layer" **tidak bisa direkonstruksi retroaktif**. User diberi 2 opsi (approksimasi 1-baris-rata-rata vs akurat-penuh-tapi-lebih-besar) — **pilih akurat penuh**.
2. **Average** (baru ketauan belakangan, LEBIH besar dari dugaan awal): costing method ini **sama sekali tidak punya audit trail** — `_stock_receive`/`_stock_consume` cuma mutate 2 field running (`qty_on_hand`/`avg_cost`) tanpa nyimpan record apa pun. Average itu **default company** (bukan FIFO!), jadi ini bukan edge case kecil — tanpa fix ini, Kartu Stok tidak jalan sama sekali di kondisi default. User dikonfirmasi lagi, lanjut fix penuh.

**Yang dikerjakan**: 2 model audit log baru — `c18.stock.consumption` (breakdown per-layer per transaksi keluar FIFO, `layer_id` FK `ondelete='restrict'`) dan `c18.stock.movement` (audit trail generik utk Average, qty signed). `product.py`: `_stock_consume`/`_stock_consume_latest`/`_stock_receive` diubah nulis ke tabel-tabel ini (helper baru `_consume_layers()` & `_log_average_movement()`). **5 tempat pemanggil diupdate** kirim `res_model`/`res_id`/`date`: `sale_delivery.py`, `sale_invoice.py`, `stock_consume.py`, `stock_opname.py`, `purchase_return.py`.

**Laporan baru** (file terpisah `stock_report.py`/`stock_report.py` controller, pola arsitektur sama): `get_stock_card_data()` (Kartu Stok, baca dari layer+consumption kalau FIFO / movement kalau Average) dan `get_inventory_balance_data()` (Saldo Persediaan, ringkasan semua produk). Menu "Reports > Stock Card" & "Reports > Inventory Balance".

**Diverifikasi ekstra hati-hati** (mesin costing itu kode kritis, dites terpisah dari laporan):
- Unit test 2-layer FIFO manual (produk baru, 2 layer harga beda, konsumsi lintas keduanya) — **split per layer benar**: 10 unit @1000 + 5 unit @1500 = 2 baris audit log, total 17.500, cocok persis.
- Full-cycle test 2x (`test-01` di-switch sementara ke `costing_method='fifo'`, generate demo, verifikasi, cleanup, **dikembalikan ke `average`** — lalu diulang test di `average` juga) — Kartu Stok & Saldo Persediaan cocok persis di KEDUA metode costing, dan cocok ke Trial Balance (akun Persediaan = 7.000.000).
- **Bug ditemukan & diperbaiki saat cleanup**: script `cleanup_demo.py` sempat gagal FK violation 2x (lupa hapus `stock.consumption` sebelum `stock.layer`, lalu lupa `stock.movement` sebelum `product`) — diperbaiki, urutan hapus yang benar: moves → stock_consumptions → stock_layers → stock_movements → product → partners → tag.

**Keterbatasan diketahui & didokumentasikan**: filter `cost_center_id` di Kartu Stok **tidak diimplementasikan** — tabel audit stok tidak menyimpan cost center, nambahnya butuh ubah skema 3 tabel + semua pemanggil, di luar scope sesi ini.

`06-accounting-business.md` poin F & `00-status-requirement.md` diupdate mencerminkan status selesai penuh.

**Pola mode 12-Bulan**: tiap mode 12-Bulan **reuse method 1-periode yang sudah ada** (dipanggil 12x, bukan tulis ulang rumus) — konsisten prinsip "1 sumber kebenaran" yang dipegang sepanjang sesi ini. Trial Balance & Neraca 12-Bulan tabelnya **kumulatif per kolom** (akun Neraca permanen, akun Laba Rugi kumulatif-sejak-1-Jan); Laba Rugi 12-Bulan **independen per kolom** (beda sifat, sudah didokumentasikan eksplisit di 09 supaya tidak salah asumsi). Trial Balance 12-Bulan lebar 24 kolom (Debit/Kredit×12), Neraca/Laba Rugi 12-Bulan pakai 1 kolom nilai per bulan — semua pakai **freeze kolom kiri** (`position: sticky` CSS, `.o_c18_yearly_table`/`.o_c18_freeze_col`, di-share lintas 3 komponen).

Semua model logic di 1 file baru `app/mvp/c18_basic_erp/models/financial_report.py` (`c18.account.financial.report`), controller di `controllers/financial_report.py`, komponen OWL di `static/src/report/*.js/.xml/.scss` (assets baru didaftarkan di manifest, sebelumnya modul ini tidak punya key `assets` sama sekali). Trial Balance 12-Bulan pakai tabel 24 kolom (Debit/Kredit×12 bulan) dgn **freeze 2 kolom kiri** (`position: sticky` CSS) — bentuknya kayak "Kertas Kerja/Neraca Lajur" akuntansi tradisional.

**Metodologi verifikasi konsisten dipakai berulang kali**: tiap laporan selesai dibangun → generate 13 transaksi demo (`c18.basic.erp.demo.generator`) ke `test-01` → panggil method via `odoo shell`, cross-check angka manual/ke laporan lain yang sudah diverifikasi duluan → **semua laporan saling cocok persis** (Trial Balance ↔ Buku Besar ↔ Neraca ↔ Laba Rugi ↔ Buku Bantu ↔ Perubahan Ekuitas) → **hapus lagi 13 transaksi demo itu dari `test-01`** (`cleanup_demo.py`, sudah dipakai berkali-kali, `test-01` selalu dikembalikan bersih setelah tiap verifikasi).

**Bug ditemukan & diperbaiki saat coding**: awal implementasi Laba Rugi sempat pakai teknik string-parsing (`float(row['amount_fmt'].replace(...))`) buat balik tanda angka - direfactor jadi parameter `sign` eksplisit di helper `_section()`, lebih bersih & tidak fragile.

**Keterbatasan diketahui & didokumentasikan** (bukan bug, edge case yang sengaja belum ditangani): Laporan Perubahan Ekuitas bisa salah hitung kalau rentang tanggal yang dipilih melintasi tanggal Tutup Buku (closing entry ikut kehitung dobel) — aman untuk kasus umum (periode tidak melintasi Tutup Buku).

`06-accounting-business.md` poin 3 & `00-status-requirement.md` diupdate menunjuk ke dokumen baru + status implementasi.

**Diverifikasi** ke database test terpisah (dihapus setelah selesai): 13 dokumen posted, 10 jurnal, stok produk sesuai perhitungan (20−10=10), idempotency teruji (panggil 2x tidak dobel). Dokumentasi lengkap: [`erd/mvp/08-demo-data.md`](../../erd/mvp/08-demo-data.md). `test-01` sudah disinkronkan (`-u c18_basic_erp` + restart).

### 12. Sistem Pencatatan Persediaan Perpetual/Periodik — BARU, SELESAI diimplementasikan & diverifikasi
Mulai dari pertanyaan simpel user ("kalo diubah jadi FIFO aja defaultnya") yang berkembang jadi 3 keputusan berurutan:

1. **`costing_method` default diubah FIFO** (sebelumnya Average) — cuma berlaku company/database **baru**, TIDAK retroaktif ke `test-01` yang sudah ada (default field baru cuma dipakai saat create record baru, bukan migrate existing row).
2. **Field `costing_method` tadinya tidak ada di UI sama sekali** (cuma bisa diubah lewat `odoo shell`) — ditambah tab baru **"ERP Settings"** di form `res.company` (menu baru **Accounting > Configuration > Company Settings**, reuse action `base.action_res_company_form`). Nama tab sengaja dibuat generik (bukan "Account Parameter" seperti pernah dipakai user di modul lain) supaya ke depan bisa nampung default lain juga (mis. default akun piutang/hutang).
3. **Sistem Pencatatan Persediaan Perpetual vs Periodik** — field baru `inventory_system` di company (default **Perpetual**, beda dari `costing_method` yang default-nya diubah — field ini BARU jadi backfill Odoo otomatis isi semua row existing dengan default, termasuk `test-01`). User pilih **"Implementasikan penuh"** (bukan cuma UI dekoratif) setelah dikasih tau field ini sebelumnya cuma dokumentasi ERD tier Standard+ yang belum ada kode sama sekali.

**Desain Periodik** (dikonfirmasi user via 2 pertanyaan AskUserQuestion, detail lengkap di [06-accounting-business.md poin F.3](../../erd/mvp/06-accounting-business.md)):
- Qty tetap real-time (validasi stok cukup/tidak & Kartu Stok qty tetap jalan), tapi **tidak ada FIFO layer/avg_cost/jurnal HPP-Persediaan per-transaksi** — mesin costing FIFO/Average nonaktif total selama mode ini.
- Akun baru **"Pembelian" (5-1100)** — Penerimaan Barang debit ke sini (bukan Persediaan).
- 3 field baru di `c18.product`: `periodic_purchases_qty`/`_value` (akumulator sejak opname terakhir), `periodic_book_value` (Persediaan Awal utk formula berikutnya).
- Transaksi sisi keluar (Pengiriman, Penjualan langsung, Pemakaian Sendiri, Retur Customer) **tanpa jurnal sama sekali** selama periode berjalan — cuma qty berubah, `move_id` kosong tapi `state='posted'`.
- **Retur Vendor** khusus tetap tercatat nilai (reverse dari pool Pembelian pakai harga rata-rata) krn mengurangi pembelian yang sudah diakui.
- **Stok Opname jadi titik penutupan periodik** — field baru `unit_cost` (input manual, default `_last_cost()`), posting jurnal 3-baris: kredit penuh Pembelian, sesuaikan Persediaan ke nilai akhir, HPP sbg angka penyeimbang (= Persediaan Awal + Pembelian − Persediaan Akhir).

**File yang diubah**: `res_company.py` (2 field baru), `product.py` (`_stock_receive`/`_stock_consume`/`_stock_consume_latest` semua ditambah branch periodik + param `add_to_purchases_pool`), `stock_opname.py` (`action_post` dipecah jadi `_action_post_perpetual`/`_action_post_periodic`, field baru `unit_cost`+`inventory_system` related), `purchase_receipt.py`/`purchase_return.py` (akun debit/kredit branch Persediaan vs Pembelian), `sale_delivery.py`/`stock_consume.py` (skip create move kalau amount 0), `sale_return.py` (cost_amount 0 + skip move kalau periodik & belum invoice), `account_account_data.xml` (akun baru `acc_5_1100`), `res_company_views.xml` (baru, tab "ERP Settings" + menu "Company Settings"), `stock_opname_views.xml` (field `unit_cost` conditional).

**Diverifikasi lengkap** via `odoo shell` (`test_periodic.py`, savepoint+rollback, tidak nyampah ke `test-01`): siklus penuh Penerimaan Barang (100 unit @1000) → Pengiriman (30 unit, no journal) → Stok Opname (fisik 65, unit_cost 1000) menghasilkan HPP **35.000** (= 0+100.000−65.000) persis sesuai formula, jurnal 3-baris balance (Dr Persediaan 65.000, Dr HPP 35.000, Cr Pembelian 100.000). Plus test Retur Vendor (5 unit dari pembelian ke-2 @1200) — pool Pembelian berkurang benar (18.000, sisa 15 unit) dan kredit ke akun Pembelian (bukan Persediaan) 6.000. Regresi cek: `test-01` existing company otomatis dapat `inventory_system='perpetual'` (backfill field baru), `costing_method` existing tidak ikut berubah (masih `fifo` dari switch manual sesi sebelumnya) — konsisten prinsip "field baru di-backfill, field existing dgn default berubah TIDAK retroaktif".

**Susulan (2026-08-30)**: user tanya "kalo periodik akun Pembelian ada, kalo perpetual gak ada kan?" — dijelaskan akun `5-1100` selalu ada di CoA (data master statis, tidak bisa dibuat kondisional saat load module), tapi user minta dibuatkan **auto archive/unarchive** biar tidak membingungkan. Diimplementasikan: `res.company.write()` override — tiap kali `inventory_system` diubah, cari akun `5-1100` company tsb & toggle `active` (Periodik→aktif, Perpetual→archive). Default fresh-install `active=False` (konsisten default `inventory_system='perpetual'`). Diverifikasi via `odoo shell` (savepoint+rollback): toggle 2 arah bekerja benar.

**Belum dikerjakan** (di luar scope permintaan user kali ini, dicatat sbg potensi lanjutan): validasi "cuma boleh ganti `inventory_system`/`costing_method` setelah tutup buku" (aturan sudah didokumentasikan di ERD sejak awal, belum ada enforcement kode - sama seperti `costing_method` sebelumnya, gap lama bukan baru). Kartu Stok/Saldo Persediaan belum dicoba tampilannya saat mode Periodik aktif (kolom nilai kemungkinan kosong/nol krn tidak ada layer/movement, sesuai desain, tapi belum ada smoke test UI-nya).

**Insiden setelah deploy - dicatat sbg gotcha operasional (bukan bug kode)**: user buka menu "Company Settings" di browser, kena error `OwlError: "res.company"."inventory_system" field is undefined`. Dicek server-side (`fields_get`/`get_view` via `odoo shell`) — field & arch view **sudah benar**, bukan bug. Penyebab: seluruh update module sesi ini dijalankan lewat `docker compose exec ... odoo -u ... --stop-after-init` (proses CLI terpisah, `--no-http`) — proses itu APPLY perubahan ke database, tapi **server yang sedang jalan melayani browser di `localhost:8069` adalah proses LAIN** yang registry-nya di memori masih versi lama, tidak otomatis sinkron. Fix: `docker compose restart odoo18-erp`. **Pelajaran buat sesi depan**: tiap kali update module lewat `-u` yang mengubah Python field/view (bukan cuma data), WAJIB restart container setelahnya kalau mau langsung dicek di browser yang sedang jalan - bukan cuma opsional kayak yang ditulis di `cara-buat-database-baru.md` poin 5 sebelumnya (poin itu perlu direvisi jadi lebih tegas, bukan "restart kalau perlu").

### 13. Skenario Testing PT Roda Sejahtera Dijalankan Penuh (via script, bukan klik manual) — TODO #1 SEBAGIAN SELESAI
User minta "jalankan testing transaksi" — karena tidak ada tool browser automation, dijalankan sebagai script `odoo shell` (bukan klik manual di UI, disepakati via AskUserQuestion) yang mereplikasi SELURUH isi [`testing/mvp/01-transaksi-distributor-ban.md`](../../testing/mvp/01-transaksi-distributor-ban.md) — 17 bulan transaksi (Nov 2024-Apr 2026) + batch gap-coverage Maret 2026 (G.1-G.6) + 3 edge case (X1-X3). Dijalankan ke database **baru khusus `test-roda`** (bukan `test-01`, sesuai instruksi eksplisit prosedur testing yang minta database terpisah) — `base`+`c18_theme`+`c18_basic_erp`, IDR/Indonesia, `costing_method=fifo` sesuai skenario.

**Hasil: SEMUA PASS, ter-commit ke `test-roda`** — checkpoint prepaid rent, FIFO 2-layer, retur+refund nominal negatif, write-off, Uang Muka+apply DP, Retur Vendor+refund, Stok Opname, 9 SKU qty (checkpoint interim & akhir), Laba Ditahan sebelum/sesudah Tutup Buku 2025 (berubah dari 42.933.000 → 302.952.132, membuktikan proses jalan), X1 (tolak oversell), X2 (FIFO 17.500 vs Average 18.750, beda sesuai teori), X3 (penguncian periode).

**2 bug nyata ditemukan & diperbaiki selama proses ini**:
1. **Bug produk serius (crash instalasi database baru manapun)**: `res_company_views.xml` (dari kerjaan sesi ini sebelumnya - poin 12) punya `<menuitem parent="menu_c18_basic_erp_config">`, tapi menu itu didefinisikan di `menu.xml` yang di-load **setelah** `res_company_views.xml` di urutan `data` manifest — install baru (belum pernah punya menu itu di database) langsung crash total (`ParseError`/`ValueError: External ID not found`). Lolos tak terdeteksi di `test-01` karena menu itu **sudah ada** dari install sebelumnya (update `-u` beda dari install `-i` fresh). **Fix**: pindahkan `<menuitem>` dari `res_company_views.xml` ke `menu.xml` (tempat semua menuitem lain memang berada), bukan cuma reorder manifest.
2. **Gotcha (bukan bug user-facing)**: `c18.sale.writeoff`/`c18.purchase.writeoff` field `amount` cuma otomatis keisi lewat `@api.onchange` — aman dipakai manual di browser (onchange jalan normal saat user pilih invoice/bill di form), tapi `create()` programatik langsung (script/API, seperti script testing ini) HARUS isi `amount` eksplisit atau kena `NotNullViolation`. Dicatat sbg referensi kalau nanti scripting serupa lagi.
3. **Bug arithmetic di dokumen skenario sendiri (bukan kode)**: `01-transaksi-distributor-ban.md` checkpoint bilang sewa 120jt/tahun (10jt/bulan) lunas dalam **10 bulan** (Nov24-Agu25) — matematisnya salah, 10×10jt=100jt bukan 120jt, butuh **12 bulan** (sampai Okt25) baru benar Rp 0. `00-skenario-distributor-ban.md` (dokumen induk) sebenarnya **sudah benar** dari awal ("Jan-Okt 2025, 10 bulan" - total 12 bulan dgn Nov+Des 2024), cuma tabel transaksi detailnya (01) yang menyimpang berhenti di Agustus. **Fix** (dipilih user, opsi "perpanjang ke 12 bulan"): tambah 2 baris amortisasi (September=bulan 11, Oktober=bulan 12) di 01, hapus catatan "tidak ada amortisasi September" yang jadi tidak berlaku lagi, pindah checkpoint saldo Rp 0 dari 31 Agu ke 31 Okt 2025. Diupdate juga di `02-prosedur-testing.md` poin 4.

**Batasan yang jujur dilaporkan**: ini memvalidasi **logic/data backend end-to-end**, BUKAN UI/UX (tidak ada tool browser automation tersedia) — tidak menangkap bug tampilan/rendering/JS seperti `OwlError` yang terjadi terpisah di poin 12 di atas. Klik-manual sungguhan di browser (tujuan asli TODO #1) masih belum dilakukan, jadi TODO #1 ditandai **sebagian selesai**, bukan tuntas penuh.

Script test (`test_roda_full.py`, ~500 baris, helper function per jenis dokumen: `kas_masuk`/`kas_keluar`/`jurnal_umum`/`po_cycle`/`so_cycle`/`payroll_full`) ada di scratchpad sesi ini — belum dipindah ke repo permanen, tulis ulang kalau perlu lagi (pola persis mengikuti isi tabel `01-transaksi-distributor-ban.md`, section per section).

### 14. Mode B PT Roda Sejahtera — Skenario Alternatif yang Laba (2026-08-30)
Setelah TODO #1 (progres poin 13) dijalankan, user tanya "hasil laba ruginya = rugi ya?" — dicek: **rugi kedua tahun** (2024: rugi 42.933.000; 2025: rugi 260.019.132) di skenario Mode A (`test-roda`). Sebabnya: beban tetap bulanan (gaji 2 karyawan + sewa + listrik/internet ≈ Rp 23-24 juta/bulan) jauh lebih besar dari laba kotor volume kecil (margin ~16%, cuma 2x jual/bulan).

User minta dibuatkan skenario alternatif yang lebih sehat, dengan syarat bisnis: **harga jual TIDAK boleh naik** (alasan: bisnis baru berdiri, prioritas jaga pelanggan) — sempat berubah pikiran di tengah diskusi (markup 40% akhirnya diterima), lalu setelah lihat hasil awal (masih rugi) user tegaskan **2025 wajib laba**, 2024 boleh tetap rugi.

**Proses iteratif** (detail lengkap tiap percobaan ada di [01-transaksi-distributor-ban.md](../../testing/mvp/01-transaksi-distributor-ban.md#mode-b--volume-sehat--markup-lebih-wajar-2026-08-30-revisi-final)):
1. HPP landai (1-2%/3bulan, bukan 3.5-4.5%) + qty ×3, harga jual tetap → rugi 2025 turun ke 216jt, masih jauh dari impas.
2. Estimasi murni-via-qty butuh ×13 (tidak realistis) → dipertimbangkan ulang markup jual.
3. Markup 40% (dari harga beli dasar tiap SKU) + qty ×5 → 2024 nyaris impas, **2025 masih rugi 44jt**.
4. Dihitung ulang titik impas **presisi** (bukan estimasi linear lintas-mode yang meleset ~55jt sebelumnya) — langsung dari Fixed cost aktual: **m=5,793**. Naik ke qty ×6.
5. **Hasil final**: KEDUA tahun laba (2024: +6.817.000, 2025: +3.386.868).

**Keputusan penamaan**: sempat mau dibuat "Mode C" (database terpisah `test-roda-v3`) supaya tiap percobaan tersimpan sbg titik data berbeda, tapi user minta **tetap "Mode B"** (revisi, bukan mode baru) — `test-roda-v3` & versi awal `test-roda-perpetual-fifo` (qty×3 tanpa markup) di-drop, digantikan versi final langsung di `test-roda-perpetual-fifo`.

**3 database final yang hidup sekarang**: `test-roda` (Mode A, rugi, tidak diubah), `test-roda-perpetual-fifo` (Mode B, qty×6+markup40%+HPP landai, LABA kedua tahun). Semua checkpoint (stok, deduction, write-off, DP/retur, X1/X3) PASS di kedua database. Script Python di scratchpad sesi ini: `test_roda_full.py`(Mode A), `test_roda_v3.py`(draft qty×5, superseded), `test_roda_v2_x6.py`(Mode B final, qty×6) — dibuat via transform terprogram dari Mode A (regex kalikan qty di tuple `('BAN-X', qty, price)`), bukan ditulis ulang manual, utk kurangi risiko salah ketik di 50+ baris transaksi.

**Pelajaran metodologi**: estimasi titik impas via regresi linear lintas-2-mode-berbeda-margin (Mode A costing vs Mode B) MELESET jauh (prediksi laba 11jt, aktual rugi 44jt) — begitu dihitung ulang dari SATU titik data yang konsisten (Fixed cost aktual di database, bukan estimasi silang), presisinya jauh lebih baik (prediksi laba 11,5jt di m=6, aktual laba 3,4jt - beda tipis, arah benar).

### 15. 4 Tema Perpetual/Periodik × FIFO/Average — Validasi Nyata Pertama utk Fitur Periodik (2026-08-30)
Lanjutan poin 14. User tanya status axis lain (Perpetual vs Periodik, FIFO vs Average) di skenario — ternyata FIFO/Average cuma pernah dites lewat edge case kecil (X2), dan **Periodik belum pernah lewat skenario bisnis nyata sama sekali** (cuma unit test 1 produk beberapa transaksi, `test_periodic.py` progres poin 12).

**Temuan teknis penting (dari cek ulang kode)**: begitu `inventory_system=periodic` aktif, `costing_method` (FIFO/Average) **sama sekali tidak dibaca** oleh mesin costing (`product.py` branch ke jalur periodik duluan, sebelum sempat cek `costing_method`). Jadi dari 4 kombinasi yang kelihatan mungkin, cuma **3 yang beda perilaku secara nyata** — Periodik-FIFO dan Periodik-Average pasti identik. Ini dikonfirmasi ke user SEBELUM eksekusi (bukan ditemukan pas sudah kadung jalan), lalu **dibuktikan empiris juga** (jalankan 2x, hasil sama persis sampai rupiah terakhir).

**Keputusan user**: harga cuma pakai **Mode B** buat semua tema ke depan (Mode A tidak diperluas lagi, cukup 1 database historis).

**Yang dikerjakan**:
- Tema 1 (Perpetual-FIFO, `test-roda-perpetual-fifo`) & Tema 2 (Perpetual-Average, `test-roda-perpetual-avg`) — **tidak butuh perubahan skenario sama sekali**, cuma beda 1 setting `costing_method` company saat setup, script Python identik 100%.
- Tema 3 (Periodik-FIFO, `test-roda-periodik-fifo`) — butuh tambahan desain: **jadwal closing Stok Opname tahunan** (krn HPP di Periodik cuma diakui saat Opname, bukan per-transaksi). Dirancang: 31 Des 2024 (5 SKU yang sudah pernah dibeli), 31 Des 2025 (semua 9 SKU), qty fisik = qty sistem (tanpa selisih, murni pengakuan nilai). Opname G.4 yang sudah ada (C1, Maret 2026) dipertahankan, cuma ditambah `unit_cost` eksplisit (wajib diisi manual di mode ini, beda dari Perpetual yang otomatis baca `_last_cost()` dari layer FIFO yang di Periodik memang kosong total).
- Tema 4 (Periodik-Average, `test-roda-periodik-avg`) — script SAMA PERSIS dgn Tema 3, cuma ganti `costing_method`, dijalankan buat pembuktian empiris.

**Hasil (semua PASS, semua checkpoint stok identik krn qty_on_hand tetap real-time di semua mode)**:

| Tema | 2024 | 2025 |
|---|---|---|
| Perpetual-FIFO | Laba 6.817.000 | Laba 3.386.868 |
| Perpetual-Average | Laba 6.817.000 | Laba 1.673.178 |
| Periodik-FIFO | Laba 6.817.000 | Laba 4.346.868 |
| Periodik-Average | Laba 6.817.000 | Laba 4.346.868 (identik Periodik-FIFO) |

2024 identik di SEMUA tema (masuk akal — total HPP setahun sama, cuma beda waktu pengakuannya, dan 2024 cuma 2 bulan tanpa kompleksitas). 2025 bervariasi wajar sesuai mekanisme masing-masing metode, semua tetap arah LABA.

**Nilai validasi**: ini pertama kalinya fitur Periodik (dibangun sesi ini, poin 12) diuji lewat skenario bisnis multi-bulan multi-SKU yang realistis, bukan cuma unit test kecil — meningkatkan keyakinan fitur ini benar jauh lebih tinggi dari sebelumnya. Verifikasi tambahan: `c18.stock.layer` (tabel FIFO) dicek 0 baris sepanjang skenario Periodik — konfirmasi mesin FIFO nonaktif total, bukan cuma kebetulan tidak kepakai.

**6 database final yang hidup sekarang** (semua di server lokal, bukan cuma catatan): `test-01` (kerja utama, kosong), `test-roda` (Mode A historis, rugi), `test-roda-perpetual-fifo` (Tema 1, Perpetual-FIFO+ModeB), `test-roda-perpetual-avg` (Tema 2, Perpetual-Average+ModeB), `test-roda-periodik-fifo` (Tema 3, Periodik-FIFO+ModeB), `test-roda-periodik-avg` (Tema 4, Periodik-Average+ModeB). Script Python scratchpad final: `test_roda_v2_x6.py` (Tema 1&2, dipakai jg utk Tema 2 tinggal ganti setting), `test_roda_periodic.py` (Tema 3&4).

### 16. Dokumen Testing Dirapikan — Label "Mode A/B" Dihapus (2026-08-30)
Setelah 4 tema selesai (poin 15), user minta dokumen `testing/mvp/00-`/`01-transaksi-distributor-ban.md`/`02-prosedur-testing.md` dirapikan: **hapus semua label "Mode A"/"Mode B"**, jadikan angka final (qty ×6 + markup 40% + HPP landai — yang sebelumnya disebut "Mode B") sebagai **satu-satunya** angka yang ditulis di dokumen (tanpa embel-embel nama "Mode B"), dan struktur dokumen diputar ke sekitar **4 tema**.

**Yang dikerjakan**: seluruh tabel transaksi kronologis (~150 baris, Nov 2024-Apr 2026) ditulis ulang dari 0 — bukan hitung manual, tapi **digenerate lewat script Python** (`gen_markdown.py`, scratchpad) yang qty/harga-nya di-*parse* langsung dari `test_roda_v2_x6.py` (script yang SUDAH terverifikasi lolos assertion Odoo) — supaya angka baru di markdown pasti konsisten dengan angka yang sudah dites, bukan hasil hitung ulang manual yang rawan salah (sempat ketemu 5 bug hitung manual di draf generator awal, semua ketauan & diperbaiki via cross-check ke script asli sebelum ditulis ke dokumen final).

- `01-transaksi-distributor-ban.md`: full rewrite — 1 skema harga beli (landai), 1 tabel harga jual (markup 40%), seluruh tabel bulanan pakai qty/nominal final, checkpoint stok (interim & akhir per SKU) dihitung ulang & diverifikasi cocok 100% dengan `expected_interim`/`expected_final` dict di script asli.
- `00-skenario-distributor-ban.md`: tabel Master Produk & poin E disederhanakan, tidak ada lagi split Mode A/B.
- `02-prosedur-testing.md`: Ringkasan Checklist ditulis ulang pakai angka Tema 1 (Perpetual-FIFO) sbg acuan, tanpa naratif Mode A/B.

**`test-roda` sempat TIDAK dihapus** (tetap ada sbg data eksplorasi) — tapi lihat poin 18 di bawah, akhirnya di-drop juga di penghujung sesi atas permintaan eksplisit user. Narasi lengkap perjalanan Mode A→B (poin 14 di atas) tetap dipertahankan di file ini sbg log keputusan, cuma dihapus dari dokumen `testing/mvp/` yang jadi spec resmi ke depan.

### 17. Gap Drill-Down Jurnal Ditemukan & Diperbaiki (2026-08-30)
User cek jurnal hasil eksekusi skenario, nemu 2 hal:
1. **Buka menu "General Journal" cuma kelihatan 25 entri** — sempat dikira bug/data hilang. Dicek: **bukan bug** — menu itu memang sengaja `domain=[('journal_id.code','=','JU')]`, cuma nampilin tipe Jurnal Umum (Amortisasi/koreksi/dst), bukan SEMUA jurnal. Total jurnal sebenarnya 246 (dibuktikan lewat query `odoo shell`), tersebar di banyak menu lain (Kas Bank, Pembelian, Penjualan, Payroll, dst) sesuai jenis dokumen sumbernya masing-masing.
2. **Form Kas Masuk/Kas Keluar (dan hampir semua dokumen sumber lain) tidak punya cara lihat jurnal hasil posting-nya** — field `move_id` ADA di model tapi tidak ditampilkan di view. Dicek: dari ~19 model yang generate jurnal, cuma **1** (`c18.account.closing`/Tutup Buku) yang sudah nampilin `move_id` di form-nya.

User juga tanya soal **laporan aging piutang/hutang** — dicek: **tidak ada fitur ini sama sekali** di sistem (bukan kelewat, tapi keputusan scope eksplisit yg sudah didokumentasikan dari 2026-08-26 di [erd/mvp/06-accounting-business.md:109](../../erd/mvp/06-accounting-business.md#L109) — "Field aging/umur hutang per invoice — dikonfirmasi tidak perlu"). Skenario yang semua piutang/hutangnya lunas TIDAK melewatkan pengujian apapun soal ini, krn memang tidak ada laporan aging yang perlu diuji.

**Yang diperbaiki**:
- Field `move_id` (readonly) ditambahkan ke **18 form dokumen sumber** yang sebelumnya tidak menampilkannya: Kas Masuk/Keluar/Transfer, Penerimaan Barang, Vendor Bill, Pembayaran Vendor, Uang Muka Pembelian, Retur Vendor, Write-off Hutang, Pengiriman Barang, Customer Invoice, Penerimaan Piutang, Uang Muka Penjualan, Retur Customer, Write-off Piutang, Aktiva Tetap, Payroll (Pengakuan & Pembayaran), Pemakaian Sendiri, Stok Opname.
- Menu baru **"Journal Entries"** — awalnya di bawah Accounting root, lalu dipindah user ke bawah **Reports** (`menu_c18_basic_erp_reports_root`, sequence 140) — nampilin SEMUA `c18.account.move` tanpa filter journal, buat browsing/drill-down bebas.
- View list+form KHUSUS untuk menu itu dibuat **read-only** (`view_c18_basic_erp_move_list_readonly`/`_form_readonly`, atribut `create="0" edit="0" delete="0"`, tanpa tombol Post/Reset) — atas permintaan user, krn menu itu murni buat lihat, bukan input. "General Journal" (menu asli, khusus JU) TETAP bisa create/edit seperti biasa lewat view aslinya (view berbeda, action beda, sama-sama model `c18.account.move`).
- Semua 4 database tema disinkronkan + server di-restart supaya browser langsung kepakai.

### 18. Housekeeping Database Akhir Sesi — Rename & Cleanup jadi 4 Database (2026-08-30)
User minta 2 hal:
1. **Rename 4 database tema** biar nama-nya selaras istilah skenario: `test-roda-v2`→**`test-roda-perpetual-fifo`**, `test-roda-avg`→**`test-roda-perpetual-avg`**, `test-roda-periodic`→**`test-roda-periodik-fifo`**, `test-roda-periodic-avg`→**`test-roda-periodik-avg`**. Dieksekusi via `ALTER DATABASE ... RENAME TO ...` (koneksi aktif diputus dulu tiap database sebelum rename). Semua referensi nama lama di `01-transaksi-distributor-ban.md`/`02-prosedur-testing.md`/`00-skenario-distributor-ban.md`/file ini disinkronkan ke nama baru.
2. **"sisain 4 aja sesuai tema"** — awalnya ditanya balik apakah `test-01` (database kerja umum, beda tujuan dari skenario) ikut di-drop atau dipertahankan; user jawab **ikut di-drop juga** — jadi cuma tersisa PERSIS 4 database di server sekarang, tidak ada database lain sama sekali. `test-01` dan `test-roda` di-drop pakai `DROP DATABASE` (koneksi aktif diputus dulu).

**Implikasi utk sesi depan**: kalau butuh database kerja umum lagi (bukan bagian skenario PT Roda Sejahtera), harus bikin baru dari 0 (lihat [`cara-buat-database-baru.md`](cara-buat-database-baru.md)) — tidak ada lagi `test-01` yang siap pakai.

## Temuan Gap (Dicatat, Belum Diperbaiki)
- **Fixed Asset reconciliation, edge case minor**: `_check_coa_reconciliation` di `fixed_asset.py` menjumlah SEMUA baris debit dari akun bertipe `fixed_asset` (termasuk Akumulasi Penyusutan, karena satu tipe yang sama) untuk dibanding ke total Acquisition — aman untuk alur normal, tapi kalau nanti ada transaksi Disposal/Sale yang men-debit Akumulasi Penyusutan, bisa memicu warning mismatch palsu. Belum diperbaiki, prioritas rendah, dicatat sebagai referensi kalau nanti ketemu warning aneh pas testing Disposal.

## Keputusan Besar yang Perlu Diingat
1. **UI `c18_basic_erp` full Inggris** (label, menu, error, help text, DAN kode teknis Selection seperti `account_type`) — kecuali nama akun/journal di data master yang tetap Indonesia. Ini konvensi baru untuk modul ini ke depan, beda dari asumsi awal proyek yang sepenuhnya Bahasa Indonesia.
2. **Tutup Buku dalam skenario testing tidak harus langsung diproses di akhir tahun** — pola "ditunda" (seperti 2025) valid untuk skenario yang sengaja mau amati efek before/after ke Laba Ditahan, beda dari pola default (2024) yang langsung ditutup.
3. **`c18_help` bukan kandidat auto-install** — sifatnya tools QA/testing internal, bukan bagian produk yang dijual ke client. Kalau nanti ada User Guide client, itu modul/folder terpisah.
4. **Bikin database baru lewat CLI wajib set Country manual** — kalau lupa, currency default jadi USD (kejadian 2x sesi ini), bukan IDR.
5. **`c18_help` DIPUTUSKAN jadi permanen — tapi scope-nya cuma internal tester/QA, bukan client.** Tidak ada pembatasan hak akses saat ini (siapa pun yang login bisa buka menunya), jadi **wajib dipastikan TIDAK ikut ter-install di database demo/client** — jangan sampai kebawa cuma karena clone dari database dev. Sudah dieksekusi penuh (rename label "QA Guide", manifest, PRD) — lihat progres poin 9.
6. **Mekanisme `'demo'` bawaan Odoo TIDAK BISA dipakai untuk modul `auto_install: True`** — berlaku umum, bukan cuma `c18_basic_erp`. Kalau ke depan ada modul auto_install lain yang butuh demo data, jangan coba pola yang sama, langsung ke trigger manual (lihat progres poin 10).
7. **Pola arsitektur "report interaktif" untuk modul ini seterusnya**: `models.AbstractModel` + HTTP controller (`type='json'`) + komponen OWL custom (live `rpc()`, tanpa tombol/reload) — BUKAN wizard `TransientModel`+onchange yang sempat direncanakan. Referensinya `d:\Odoo Dev\odoo18_toso` (`c18_hr_payroll`, komponen slip gaji). Pakai pola ini lagi kalau ke depan ada laporan/report interaktif lain di luar 7 Laporan Keuangan (mis. Kartu Stok).
8. **Setiap kali ubah `financial_report.py`, WAJIB verifikasi via generate-demo → cross-check ke laporan lain yang sudah benar → cleanup demo lagi** — pola ini konsisten dipakai 7x sesi ini (lihat progres poin 11), jangan skip langkah cleanup di `test-01` (script siap pakai: lihat scratchpad sesi ini `cleanup_demo.py`, belum dipindah ke repo permanen — kalau perlu lagi sesi depan, tulis ulang berdasarkan pola di sana: hapus payment→accrual→fixed_asset→invoice→delivery→SO→bill→receipt→PO→cash→moves→stock_layers→product→partners→tag, plus clear `ir.config_parameter` demo_generated guard).

## TODO — Belum Dikerjakan / Masih Terbuka (Kandidat Sesi Berikutnya)
Sudah diberi nomor supaya gampang disebut (mis. "TODO 3"). 5 item sempat ada di daftar TODO sesi ini (sync `.rst` c18_help, tentukan database kerja, keputusan permanen/dibuang `c18_help`, rapikan status `c18_help`, demo data client) sudah **semuanya selesai** — lihat progres poin 8-10 & Keputusan Besar poin 5-6. 1 item lagi (`sub2.domain.id`) dicoret bukan karena selesai, tapi karena **di luar konteks repo ini** (repo odoo2 sendiri) — cukup dicatat di [`setting-nginx-multi-domain-ssl.md`](setting-nginx-multi-domain-ssl.md), tidak perlu di-duplikasi di sini. Sisanya dirapikan urut lagi.

Sudah diberi nomor supaya gampang disebut. **TODO 2 lama (Laporan Keuangan + Kartu Stok) sudah tuntas 100%** sesi ini (lihat progres poin 11 & 11b) — dicoret, sisanya dirapikan urut lagi.

1. [~] **Jalankan skenario testing PT Roda Sejahtera manual di UI** — **SEBAGIAN selesai (2026-08-30)**: jalur backend sudah divalidasi penuh via script `odoo shell`, di **4 kombinasi Perpetual/Periodik×FIFO/Average** (lihat progres poin 13-18), semua checkpoint PASS & LABA kedua tahun. Yang BELUM: klik-manual sungguhan di browser (tujuan asli poin ini) - script tidak menangkap bug UI/rendering/JS. Kalau mau tuntas 100%, tinggal buka salah satu dari 4 database (`test-roda-perpetual-fifo`/`-perpetual-avg`/`-periodik-fifo`/`-periodik-avg`, sudah ada 200+ jurnal/dokumen live) di browser buat spot-check tampilan form/laporan, TIDAK perlu input ulang dari nol. `test-roda` (Mode A) & `test-01` sudah di-drop, tidak ada lagi.
2. [ ] Modul `c18_stock`/`c18_purchase`/`c18_sale` (Standard tier) — belum dibuat sama sekali.
3. [ ] Riset 3 repo referensi payroll (`odoo18-toso`, `odoo18-cep`, `odoo10-kp3`) utk `07-hris.md` — **masih menggantung dari 3 sesi sebelumnya**.
4. [ ] Folder `docs/user-guide/` masih kosong — isi User Guide belum ada rencana konkret kapan dibangun.
5. [ ] Export PDF/Excel untuk Laporan Keuangan — opsional, tidak ada satupun laporan yang butuh ini utk dianggap "selesai" (lihat "Belum Diputuskan" di [09-laporan-keuangan.md](../../erd/mvp/09-laporan-keuangan.md)).
6. [ ] Filter `cost_center_id` di Kartu Stok — tidak diimplementasikan (tabel audit stok tidak menyimpan cost center), dicatat sebagai keterbatasan di [06-accounting-business.md poin F](../../erd/mvp/06-accounting-business.md#f-persediaan--mekanisme-costing-fifoaverage-2026-08-26-melengkapi-gap-belum-diputuskan-sebelumnya).

## Peta Dokumen Penting
- `app/mvp/c18_basic_erp/` — kode modul utama, UI sudah full Inggris, `account_type` sudah kode Inggris juga.
- `testing/mvp/00-skenario-distributor-ban.md`, `01-transaksi-distributor-ban.md`, `02-prosedur-testing.md` — skenario & prosedur testing, sudah full rewrite (2026-08-30): tanpa label Mode A/B, struktur di sekitar **4 tema** Perpetual/Periodik×FIFO/Average, semua checkpoint & angka final sudah terverifikasi.
- `app/mvp/c18_basic_erp/views/account_move_views.xml`, `menu.xml` — menu "Journal Entries" (read-only, semua jurnal, di bawah Reports) + `move_id` drill-down di 18 form dokumen sumber (baru, 2026-08-30, lihat progres poin 17).
- `notes/claude-notes/setting-nginx-multi-domain-ssl.md` — panduan nginx+SSL, status `sub1.domain.id` selesai.
- `notes/claude-notes/cara-buat-database-baru.md` — prosedur baku bikin database baru lewat CLI (baru, sesi ini).
- `erd/mvp/01-accounting-foundation.md` poin 5, `erd/mvp/06-accounting-business.md` poin B — diupdate sesi ini (aturan konversi multi-currency, aturan akun lawan Kas Bank).
- `erd/mvp/00-status-requirement.md` — status tracking utama, sudah diupdate (gap multi-currency closed).
- `docs/user-guide/` — folder baru, kosong, buat User Guide client nanti.
- `app/base/c18_help/` — **permanen** (bukan prototype lagi), menu "QA Guide", tidak auto-install, isi `.rst` sudah disinkronkan ulang sesi ini (regenerasi via pandoc, terverifikasi). PRD: [`erd/base/06-qa-guide-viewer.md`](../../erd/base/06-qa-guide-viewer.md).
- `app/mvp/c18_basic_erp/models/demo_generator.py` — generator demo data client (`c18.basic.erp.demo.generator._generate()`, panggil manual lewat `odoo shell`). Dokumentasi: [`erd/mvp/08-demo-data.md`](../../erd/mvp/08-demo-data.md).
- `erd/mvp/09-laporan-keuangan.md` — requirement field-level 7 Laporan Keuangan, **SEMUA 9 mode (termasuk 12-Bulan) SELESAI diimplementasikan**.
- `app/mvp/c18_basic_erp/models/financial_report.py` — `c18.account.financial.report` (`AbstractModel`), semua logic 7 laporan (9 mode) yang sudah selesai.
- `app/mvp/c18_basic_erp/models/stock_report.py` — `c18.stock.report` (`AbstractModel`), logic Kartu Stok + Saldo Persediaan.
- `app/mvp/c18_basic_erp/models/stock_consumption.py`, `stock_movement.py` — 2 model audit log baru (FIFO per-layer & Average generik) yang jadi fondasi Kartu Stok — WAJIB dibaca dulu kalau nanti ubah lagi `product.py` costing engine.
- `app/mvp/c18_basic_erp/controllers/` — HTTP controller JSON routes utk semua laporan (baru, modul ini sebelumnya tidak punya folder `controllers/` sama sekali). 2 file: `financial_report.py`, `stock_report.py`.
- `app/mvp/c18_basic_erp/static/src/report/` — komponen OWL tiap laporan, 9 pasang js/xml (baru, modul ini sebelumnya tidak punya key `assets` di manifest sama sekali).
- `app/mvp/c18_basic_erp/views/res_company_views.xml` — **baru**, tab "ERP Settings" di form Company (field `costing_method`+`inventory_system`). Menu **Accounting > Configuration > Company Settings** ada di `menu.xml` (BUKAN di file ini - pernah salah taruh di sini & bikin crash install baru, lihat progres poin 13).
- **Status database akhir sesi (2026-08-30)**: `test-01` (database kerja umum) dan `test-roda` (Mode A historis) **sengaja di-drop** atas permintaan user, supaya cuma tersisa 4 database sesuai 4 tema - kalau sesi depan butuh database kerja umum lagi (bukan bagian skenario Roda Sejahtera), harus bikin baru (lihat [`cara-buat-database-baru.md`](cara-buat-database-baru.md)). 4 database final:
- `test-roda-perpetual-fifo` — database **Tema 1** (Perpetual-FIFO + harga final: HPP naik landai, qty ×6, markup jual 40% - lihat progres poin 14/15 & [01-transaksi-distributor-ban.md](../../testing/mvp/01-transaksi-distributor-ban.md)). Hasil: **LABA** kedua tahun (2024: +6,8jt; 2025: +3,4jt). Field baru `inventory_system`/`costing_method` bisa dilihat di **Accounting > Configuration > Company Settings**, dan `move_id` tiap dokumen sumber (Kas Bank, Pembelian, Penjualan, dst) sudah bisa di-drill-down langsung dari form-nya (poin 17 di atas).
- `test-roda-perpetual-avg` — database **Tema 2** (Perpetual-Average, script identik `test-roda-perpetual-fifo` cuma beda 1 setting). Hasil: LABA (2024: +6,8jt; 2025: +1,7jt).
- `test-roda-periodik-fifo` — database **Tema 3** (Periodik-FIFO, lihat progres poin 15). Butuh jadwal closing Stok Opname tahunan tambahan (31 Des 2024 & 31 Des 2025). Hasil: LABA (2024: +6,8jt; 2025: +4,3jt). Validasi pertama fitur Periodik lewat skenario bisnis nyata.
- `test-roda-periodik-avg` — database **Tema 4** (Periodik-Average, script identik `test-roda-periodik-fifo`). Hasil **identik persis** Tema 3 (dibuktikan empiris `costing_method` diabaikan total saat Periodik aktif).
