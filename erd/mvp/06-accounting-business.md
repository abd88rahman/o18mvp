# Requirement - Accounting (Business Layer): Kas Bank, Aktiva Tetap, Laporan Keuangan (`c18_account` lanjutan)

Status: **draft direview (2026-08-26), belum diimplementasikan.**

**Tier** — lihat [erd/00-tiering-produk.md](../00-tiering-produk.md) untuk mekanisme lengkap:
- **Kas Bank (poin 1)**: fitur inti Accounting, **bukan placeholder** — 3 form spesifik (Kas Masuk/Keluar/Transfer) relevan **dari tier Basic**, bukan cuma Standard.
- **Aktiva Tetap (poin 2)**: di Basic cuma register aset polos + kelima jenis transaksinya (Pengakuan/Penyusutan/Penghapusan/Penjualan/Revaluasi) diinput manual lewat **form generic** di bawah menu "Aktiva Tetap" sendiri (bukan native/spesifik, sesuai `notes/human-notes/tiering-versi.txt` baris 21-31). Yang ditulis di poin 2 di bawah (akuisisi + penyusutan otomatis + dispose/sell/revaluasi bentuk form spesifik) itu scope **Standard**.
- **Laporan Keuangan (poin 3)**: scope **Standard+**.
- **Bank Reconciliation & Budget**: **ditunda ke tier Enterprise**, bukan bagian MVP (Basic/Standard) sama sekali.

## Beda dari 01-accounting-foundation.md
[01](01-accounting-foundation.md) itu **fondasi GL** (Chart of Accounts, Journal, Move/Move Line, Cost Center, Multi-currency, Periode) — levelnya sama seperti [`c18_common`](02-common-master-data.md), dipakai bareng modul lain. Dokumen ini levelnya beda: ini modul **"Accounting"** yang sesungguhnya, salah satu dari 5 modul MVP inti (`master-plan.txt`: Sales, Purchases, Inventory, **Accounting**, HRIS) — fitur yang langsung dipakai user Accounting sehari-hari, dibangun **di atas** fondasi `01`.

Beberapa jenis jurnal yang sudah didaftar di [01](01-accounting-foundation.md#2-journal--c18accountjournal) belum ada modelnya sama sekali — itu yang jadi scope di sini.

Referensi: proyek `odoo18_accurate` sudah pernah mengimplementasikan fitur setara ini (Kas Bank, Aktiva Tetap) — bisa jadi acuan pola, sesuai misi "fitur ERP lebih mirip `odoo18_accurate`".

## Scope

### 1. Kas Bank (tier Basic+)
Form transaksi kas/bank yang **bukan** dari piutang/hutang customer/vendor (itu sudah dicover Sales/Purchase, tier Standard):
- Kas Masuk, Kas Keluar, Transfer antar Kas/Bank.
- Referensi `odoo18_accurate`: 3 form entry terpisah, penomoran placeholder (mis. `draft-<id>`) sebelum diposting, tracing `res_model`/`res_id` ke tiap baris jurnal.
- **Workflow state: `draft` → `posted`** (bukan `draft`→`confirmed`) — karena dokumen ini langsung menghasilkan jurnal, jadi ikut konvensi state `account.move` (lihat [erd/00-konvensi-teknis.md](../00-konvensi-teknis.md) poin 5), bukan konvensi dokumen bisnis biasa.

### 2. Aktiva Tetap (Fixed Asset) — otomasi ini tier Standard
- Pengakuan (kapitalisasi) aset.
- Penyusutan (depresiasi) — **metode garis lurus saja** (straight-line), tidak perlu dukungan saldo menurun/metode lain dulu.
- Penghapusan (dispose) — aset dibuang tanpa nilai jual.
- Penjualan (sell) — aset dijual, hitung gain/loss dari selisih nilai buku vs harga jual.
- Revaluasi — penilaian ulang nilai aset. Treatment PPh Final: **cukup sediakan field pilih akun PPh + nilainya** (input manual, bukan kalkulasi otomatis kompleks).
- **Workflow state: `draft` → `posted`**, sama seperti Kas Bank (poin 1) — alasan sama, dokumen ini langsung menghasilkan jurnal.

### 3. Laporan Keuangan (tier Standard+)
**Dikonfirmasi 4 laporan**: Neraca (Balance Sheet), Laba Rugi (Profit & Loss), Trial Balance (Neraca Saldo), Buku Besar per akun (General Ledger detail). Laporan per Cost Center (lihat [01](01-accounting-foundation.md) poin 4) tetap relevan sebagai turunan/filter dari laporan-laporan ini, bukan laporan terpisah.

## Detail Requirement Tier Basic — Field-Level (2026-08-26)

Melengkapi gap yang sengaja dibiarkan terbuka di [erd/00-tiering-produk.md](../00-tiering-produk.md) ("Detail requirement Basic tier"). Semua form di bawah state-nya **`draft` → `posted`** (konvensi [00-konvensi-teknis.md](../00-konvensi-teknis.md) poin 5, karena langsung menghasilkan jurnal).

### A. Jurnal Umum (form spesifik)
- **Header**: nomor (sequence per journal, definitif — bukan placeholder — format & kode prefix lihat catatan skema nomor dokumen di bawah poin J), tanggal, `journal_id` (default Jurnal Umum), referensi/keterangan, `currency_id` + kurs (kalau bukan mata uang company, lihat [01](01-accounting-foundation.md) poin 5).
- **Line**: `account_id`, `partner_id` (opsional), `cost_center_id` (opsional), deskripsi baris, debit, kredit.
- Validasi wajib: total debit = total kredit sebelum bisa posting.

### B. Kas Bank — 3 form (Kas Masuk, Kas Keluar, Transfer)
- **Header** (sama utk ketiganya): nomor (placeholder `draft-<id>` sebelum posted, baru dapat nomor definitif dari sequence journal masing-masing pas posted — pola `odoo18_accurate`), tanggal, `account_id` kas/bank (dibatasi tipe akun "Kas Bank"), `partner_id` (opsional — bisa karyawan/pihak lain non-piutang/hutang formal), `cost_center_id`.
- **Kas Masuk & Kas Keluar** — butuh `line_ids` (1 header bisa pecah ke beberapa akun lawan sekaligus, bukan cuma 1 jumlah tunggal):
  - Tiap line: `account_id` (akun lawan — akun sumber dana/pendapatan lain-lain utk Kas Masuk, akun biaya/lawan utk Kas Keluar), keterangan (per baris), nominal.
  - Total nominal seluruh `line_ids` = jumlah yang didebit/dikredit ke akun kas header.
  - Kas Masuk: debit akun kas (header) sebesar total, kredit tiap `account_id` di `line_ids` sebesar nominal masing-masing.
  - Kas Keluar: kebalikannya — kredit akun kas (header), debit tiap `account_id` di `line_ids`.
- **Transfer** — **tidak pakai `line_ids`**, cukup field flat di header: `account_id` asal, `account_id_dest` tujuan, jumlah (nominal tunggal), keterangan (tunggal juga) — tanpa `partner_id` (transfer antar kas/bank sendiri, bukan ke pihak ketiga).
- Generic reference `res_model`/`res_id` (konvensi [01](01-accounting-foundation.md) poin 3) biasanya kosong di sini — dokumen ini diinput manual langsung, bukan digenerate dari dokumen lain.

### C. Tutup Buku — belum ada requirement sama sekali sebelum ini, scope baru (diriset dari pola Accurate Online, konsisten dengan misi "lebih mirip `odoo18_accurate`"):

- **Penyesuaian Awal Tahun**: bentuk sama seperti Jurnal Umum (header+line bebas), `journal_id` beda (menu sendiri) — **tanggal default & terkunci ke 1 Januari** tahun berjalan (bukan cuma default, user tidak bisa ganti ke tanggal lain). Kegunaan: mencatat temuan audit/koreksi tahun lalu yang **tidak bisa** lagi dibukukan ke 31 Des tahun lalu (buku sudah ditutup) tapi juga **tidak tepat** dibukukan ke tanggal berjalan tahun ini (supaya tidak mendistorsi laporan tahun berjalan) — jadi ditaruh di titik netral 1 Januari.
- **Penyesuaian Akhir Tahun**: bentuk sama seperti Jurnal Umum, `journal_id` beda — **tanggal default & terkunci ke 31 Desember** tahun berjalan. Kegunaan standar: entry adjustment akhir periode (akrual, deferral, dst; depresiasi manual Basic tetap masuk lewat form Aktiva Tetap generic di poin G, bukan di sini).
- **Tutup Buku (closing entries)** — **tanggal default & terkunci ke 31 Desember** tahun yang ditutup. Bukan input manual baris-per-baris, tapi 1 aksi/tombol "Proses Tutup Buku" yang menjalankan 2 langkah otomatis (pola Accurate Online, [dikonfirmasi](https://accurate.id/akuntansi/tutup-buku-pada-proses-akuntansi/) & [ultimasolusindo.com](https://ultimasolusindo.com/aktivitas-tutup-buku-pada-accurate-online/)):
  1. **Nolkan seluruh akun Pendapatan & Beban** (semua akun yang masuk Laporan Laba Rugi) — generate 1 jurnal penutup otomatis: debit tiap akun Pendapatan sebesar saldonya, kredit tiap akun Beban sebesar saldonya.
  2. **Selisihnya (laba/rugi bersih tahun itu) langsung dipindah ke akun "Laba Ditahan"** — bukan parkir dulu di "Laba Tahun Berjalan" lalu dipindah lagi belakangan (beda dari textbook Barat yang pakai akun perantara "Income Summary"); "Laba Tahun Berjalan" di CoA kita ([01](01-accounting-foundation.md) poin 1) tetap ada tapi fungsinya cuma sebagai **saldo berjalan real-time** (dihitung otomatis buat Laporan Laba Rugi tahun berjalan selama tahun itu belum ditutup) — begitu Tutup Buku diproses, akun ini ikut ter-nolkan bareng closing entry di atas.
  - Field: tanggal tutup buku (locked 31 Des), fiscal year yang ditutup.
  - Efek posted: periode ≤ tanggal tutup buku otomatis terkunci — tidak bisa tambah/edit/hapus jurnal apapun (termasuk Penyesuaian Akhir Tahun tahun itu) di tanggal ≤ itu (konsisten dengan [01](01-accounting-foundation.md) poin 6, "kalau tanggal transaksi jatuh di periode yang sudah ditutup, blokir"). Koreksi yang ketahuan setelah titik ini wajib lewat Penyesuaian Awal Tahun (locked 1 Jan) tahun berikutnya, bukan edit balik ke sini.

**Konfirmasi dampak ke Laporan Keuangan (2026-08-26) — 2 jenis laporan beda cara baca "Laba Tahun Berjalan":**
- **Laporan Laba Rugi** (period-range, mis. laporan tahun 2023 walau dilihat 3 tahun kemudian) — dihitung dari mutasi akun Pendapatan/Beban dalam rentang tanggal itu, **bukan** dari saldo "Laba Tahun Berjalan", jadi tetap akurat kapanpun dilihat. **Syarat teknis wajib**: jurnal penutup dari Tutup Buku (tertanggal 31 Des, jatuh di dalam rentang yang sama) **harus punya penanda khusus** (mis. `is_closing_entry` di header, atau `journal_id` bertipe "Jurnal Penutup" tersendiri) supaya query Laporan Laba Rugi bisa **mengecualikannya** — kalau tidak, jurnal penutup yang meng-nolkan akun Pendapatan/Beban ikut kehitung dan laporan malah salah nunjukin 0.
- **Neraca** (point-in-time, mis. per 30 Juni 2023) — saldo "Laba Tahun Berjalan" **tetap tampil** selama tanggal laporan **belum melewati** tanggal Tutup Buku tahun fiskal itu (yang locked 31 Des) — karena jurnal penutupnya secara teknis belum "terjadi" per tanggal tersebut. Baru ter-nolkan di Neraca kalau tanggal laporan ≥ 31 Des tahun itu (setelah Tutup Buku posted).

### D. Pembelian
**Form generik** — template dasar dipakai ulang di sini, di Penjualan (poin E), dan di beberapa jenis di Persediaan (poin F): nomor placeholder (sama pola Kas Bank), tanggal, `account_id` (bebas dipilih user, tidak dibatasi tipe tertentu di Basic), `partner_id` (opsional — relevan sebagai vendor/customer), `cost_center_id`, keterangan, jumlah → auto-generate 2 baris jurnal (debit akun A / kredit akun B) dari pilihan user; kalau butuh lebih dari 2 baris, form ini boleh dipakai dalam mode line bebas persis seperti Jurnal Umum (poin A), bedanya cuma `journal_id` default. Menu per jenis arahkan ke `journal_id` masing-masing lewat context default di action — supaya asal-usul transaksi tetap kelacak (lihat [00-tiering-produk.md](../00-tiering-produk.md) bagian "versi generik").

Catatan lintas Pembelian/Penjualan/Persediaan: "Inventory"/Persediaan di Basic **bukan** modul Inventory penuh (tidak ada Warehouse/lokasi/multi-gudang, lihat [03-inventory-foundation.md](03-inventory-foundation.md) yang tier-nya Standard+, dan tidak ada Product/UoM master, lihat [02-common-master-data.md](02-common-master-data.md)) — **tapi** tetap ada tracking qty+harga sederhana per baris PO/Penerimaan Barang, cukup buat basis hitung FIFO/Average di akun Persediaan (lihat poin F).

**Rincian per jenis** (field & akun utama default, 2026-08-26) — yang beda per jenis cuma **akun utama default** yang sudah fixed vs yang masih bebas dipilih user:

0. **Purchase Order (PO) — ringan** (dokumen non-jurnal, bukan sekadar kesepakatan di luar sistem — dikonfirmasi 2026-08-26 setelah diskusi, PO ini titik cabang aktif ke Penerimaan Barang/Pembelian/Uang Muka, beda karakter dari register Aktiva Tetap yang sengaja ditiadakan di poin G):
   - **Header**: `partner_id` (vendor, wajib), tanggal, `cost_center_id` (opsional), keterangan.
   - **`line_ids`** — **pakai `product_id`** (koreksi 2026-08-26, bukan teks bebas seperti draft sebelumnya — supaya saldo Persediaan bisa dirinci **per produk**), Many2one ke `c18.product` versi sederhana ([02-common-master-data.md](02-common-master-data.md) — tanpa UoM/kategori di Basic). Tiap baris: `product_id`, qty, harga satuan → subtotal. Total PO = jumlah semua subtotal baris.
   - Baris ini yang jadi basis hitung **FIFO/Average per produk** untuk akun Persediaan (lihat catatan costing di bawah) — **beda dari pernyataan draft awal** yang bilang Basic "tanpa tracking kuantitas/valuasi apapun"; sekarang ada tracking qty+harga per produk di level baris PO/Penerimaan Barang. Cuma produk bertipe **Barang Stok** yang masuk hitungan costing ini — Jasa & Barang Non Stok tidak nambah/kurang saldo Persediaan.
   - **State: `draft` → `confirmed`** (bukan `draft`→`posted` — PO sendiri tidak langsung menghasilkan jurnal, sesuai [00-konvensi-teknis.md](../00-konvensi-teknis.md) poin 5).
   - PO ini secara modul tetap bagian `c18_account` (bukan `c18_purchase`, Standard+) — nanti di-`_inherit` `c18_purchase` buat nambah Product/UoM/multi-warehouse & fitur penuh, pola sama seperti Partner di-extend lintas tier ([00-tiering-produk.md](../00-tiering-produk.md)). **Dipertimbangkan (2026-08-26)** pindah ke `c18_common` (modul shared master data yang lebih pas secara penamaan, krn PO & Product model baru bukan `_inherit` zero-cost kayak Partner) — **diputuskan tetap di `c18_account`**, supaya Basic cukup 1 modul yang perlu di-install (bukan 2), walau konsekuensinya `c18_account` jadi tidak murni "GL doang".
   - PO **tidak wajib** dibuat utk Penerimaan Barang/Pembelian jasa (lihat poin 2) — tapi **wajib** jadi referensi Uang Muka Pembelian (poin 3).
1. **Penerimaan Barang** — referensi `po_ref_id` (Many2one ke PO, mendukung penerimaan sebagian per baris — qty diterima bisa < qty di PO). Akun **fixed** kedua sisi: debit **Persediaan** (nilai = qty diterima × harga satuan dari baris PO), kredit **Hutang Belum Difaktur** (GRNI — akun baru di bawah tipe "Hutang Lancar Lainnya", belum tercatat sebagai Hutang Usaha resmi krn belum ada invoice vendor).
2. **Pembelian** (tagihan/invoice vendor) — kredit **Hutang Usaha** (fixed). Debit **fleksibel 2 mode**, dibedakan lewat 1 field referensi opsional `grni_ref_id` (Many2one ke record Penerimaan Barang):
   - **Diisi** (invoice menutup GRNI barang yang sudah diterima duluan) → debit otomatis **Hutang Belum Difaktur** (menutup saldo GRNI dari poin 1).
   - **Kosong** (invoice berdiri sendiri, mis. pembelian jasa/non-stok tanpa Penerimaan Barang — boleh tetap referensi `po_ref_id` langsung kalau ada PO jasa, atau tanpa PO sama sekali) → debit **bebas dipilih user** (akun Beban atau Persediaan, tergantung transaksi).
   - **2 cara isi `grni_ref_id`** (1 field, 2 entry point — bukan 2 mekanisme beda): (a) buka form Pembelian langsung, cari & pilih record Penerimaan Barang di field referensi; atau (b) dari form Penerimaan Barang, tombol **"Buat Tagihan"** yang bikin record Pembelian baru dengan `grni_ref_id`, `partner_id`, dan jumlah sudah ke-prefill otomatis (shortcut, tinggal user lengkapi/koreksi lalu simpan).
   - **`line_ids` Pembelian** (2026-08-26) — tiap baris: `product_id` (opsional, Many2one `c18.product`), keterangan (teks bebas), qty, harga satuan → subtotal.
     - Ada `po_ref_id`/`grni_ref_id`: baris ke-copy dari dokumen sumber — `product_id`, qty, harga sudah otomatis terisi, keterangan otomatis = nama produk (**tetap bisa diedit user**).
     - Tanpa referensi apapun (invoice berdiri sendiri): user isi baris manual — boleh pilih `product_id` (keterangan ikut auto-fill dari nama produk, tetap editable), **atau** kosongkan `product_id` dan isi keterangan bebas teks langsung (mis. jasa/pengeluaran ad-hoc yang belum/tidak perlu terdaftar sebagai Product).
3. **Uang Muka Pembelian** — **wajib** referensi `po_ref_id` (Many2one ke PO — dasar sistemnya, bukan cuma keterangan bebas). Debit **Uang Muka Pembelian** (fixed, akun baru di bawah tipe "Aktiva Lancar Lainnya"), kredit `account_id` **Kas/Bank** (dibatasi tipe akun "Kas Bank", dipilih user).
4. **Pembayaran Vendor** — debit **Hutang Usaha** (fixed, per baris invoice), kredit `account_id` (header, dipilih user) — nilai kreditnya net setelah deduction (lihat bawah). Pola "1 pembayaran alokasi ke banyak invoice sekaligus" ini konsisten dg [04-purchase.md](04-purchase.md) poin 2 (pola Accurate), dirinci field-nya di sini (2026-08-26):
   - **`account_id` (kredit) dilonggarkan — bukan cuma Kas/Bank (2026-08-26)**: default/kasus paling umum tetap akun tipe "Kas Bank", tapi user boleh pilih akun lain buat pelunasan **non-kas** yang genuinely bukan write-off (tidak ada gain, nilainya beneran dibayar cuma bukan lewat kas): **Piutang Usaha** (kompensasi/netting — vendor itu juga customer kita), **Persediaan** (barter — bayar hutang pakai barang), **Ekuitas/Modal** (debt-to-equity conversion), **atau Uang Muka Pembelian (poin 3)** — ini jawaban gap "gimana Uang Muka ini nanti dipakai/dinetting ke invoice akhir": tinggal pilih akun kredit = Uang Muka Pembelian di sini, mengurangi saldo uang muka itu sekaligus mengurangi Hutang Usaha invoice terkait, tanpa mekanisme/model tambahan. Bedanya dari Write-off (poin 6): di sini nilai keluar beneran setara (no gain), cuma bentuknya bukan kas.
   - **`line_ids`** (pilih invoice mana saja yang dibayar, per baris): `bill_id` (Many2one ke Pembelian outstanding milik vendor yang sama), **nilai tagihan awal** (readonly, total invoice), **nilai tagihan sisa** (readonly, invoice dikurangi pembayaran-pembayaran sebelumnya), **nominal bayar** (input user, ≤ nilai tagihan sisa), **deduction** (1 kolom angka — bukan tab terpisah).
   - **Deduction lewat wizard** (dibuka dari tombol/icon di kolom deduction tiap baris): transient model berisi `deduction_ids` (One2many), tiap baris wizard: **keterangan**, **akun** (`account_id`), **nominal** (default positif = pengurang nilai kas dibayar; kalau diisi negatif = penambah). Bisa nambah baris deduction lagi (multi-deduction, boleh beda akun sekaligus) sebelum konfirmasi wizard.
   - Kolom deduction di `line_ids` cukup nampilin **1 angka** (total net dari semua baris wizard); kalau lebih dari 1 baris atau beda akun, ada **icon "view"** di sel itu buat buka rincian (read-only breakdown per akun/keterangan).
   - Efek jurnal: tiap baris deduction jadi entry tambahan — deduction positif (pengurang) → **kredit** akun tsb (mis. Pendapatan Potongan Pembelian), deduction negatif (penambah) → **debit** akun tsb (mis. Beban Admin Bank). Total kredit Kas/Bank (header) = SUM(nominal bayar semua baris) − SUM(deduction net semua baris), tetap balance krn selisihnya masuk ke akun-akun deduction itu.
5. **Retur Barang Vendor** — kredit **Persediaan** (fixed, nilai barang berkurang). Debit **fleksibel**, dibedakan referensi opsional sama seperti poin 2: kalau retur terjadi **sebelum** invoice (masih GRNI) → debit **Hutang Belum Difaktur**; kalau **sesudah** invoice (sudah jadi Hutang Usaha resmi) → debit **Hutang Usaha**.

   **Kondisional status pembayaran invoice saat retur (2026-08-26, diriset dari pola Accurate — [help.accurate.id](https://help.accurate.id/product/accurate-online/fitur-aol/pembelian/retur-pembelian/membuat-retur-pembelian-dari-faktur-yang-sudah-lunas/), [ultimasolusindo.com](https://ultimasolusindo.com/retur-pembelian-atas-faktur-yang-sudah-dilunasi/)):** ternyata **tidak perlu 3 cabang logic berbeda** di form Retur itu sendiri — retur **selalu** dicatat dengan cara yang sama (debit Hutang Usaha/Hutang Belum Difaktur, kredit Persediaan), terlepas dari status bayar invoice-nya. Bedanya cuma di tahap **berikutnya**:
   - **Belum ada invoice** (retur atas GRNI) — tidak ada isu, GRNI memang tidak pernah "dibayar" langsung, jadi tidak ada follow-up apapun.
   - **Sudah ada invoice, belum dibayar sama sekali** — retur otomatis mengurangi "nilai tagihan sisa" invoice itu (dipakai di poin 4). Tidak ada follow-up.
   - **Sudah ada invoice, sudah dibayar sebagian/lunas** — retur tetap mengurangi Hutang Usaha invoice itu seperti biasa, walau saldonya jadi **negatif** (artinya kelebihan bayar / vendor "berhutang balik" ke kita). Ini **tidak** butuh akun/model piutang baru — cukup selesaikan lewat **Pembayaran Vendor (poin 4) yang sama**, pilih invoice yang sama, isi **nominal bayar bernilai negatif** (refund — kas/bank yang tadinya kredit jadi debit, uang masuk balik), sampai saldo invoice itu normal lagi (0 atau sesuai). `line_ids` Pembayaran Vendor (nilai tagihan awal/sisa, nominal bayar) sudah mendukung ini tanpa perlu field/wizard tambahan.
6. **Write-off Hutang** — debit **Hutang Usaha** (fixed, saldo hutang dihapuskan), kredit **Pendapatan di Luar Usaha** (fixed, akun baru "Pendapatan Lain-lain" di bawah tipe itu — hutang yang dihapus dianggap keuntungan/gain, kena Pajak Penghasilan sesuai UU PPh soal pembebasan utang).
   - **Scope diperjelas (2026-08-26)**: form ini **khusus hutang yang genuinely dibebaskan/hangus** (vendor tidak menagih lagi, tidak ada balas nilai apapun dari kita) — beda dari pelunasan non-kas (poin 4) yang nilainya beneran dibayar setara, cuma bukan lewat kas (itu **bukan** write-off, tidak ada gain).
   - **>360 hari** cuma jadi salah satu **kriteria/pemicu** kapan suatu hutang layak dipertimbangkan write-off (aging lama, vendor tidak jelas/sudah tidak beroperasi, dst) — bukan mekanisme jurnal yang beda; begitu diputuskan write-off, jurnalnya tetap sama seperti di atas berapa pun umur hutangnya. **Field aging/umur hutang per invoice — dikonfirmasi tidak perlu (2026-08-26)**, di-skip, tidak masuk scope MVP ini; identifikasi kandidat write-off dilakukan manual oleh user, bukan lewat laporan otomatis.

Akun-akun baru yang perlu ditambah ke data default CoA ([01](01-accounting-foundation.md) poin 1): **Hutang Belum Difaktur** (tipe Hutang Lancar Lainnya) dan **Uang Muka Pembelian** (tipe Aktiva Lancar Lainnya) — melengkapi gap "Belum Diputuskan" di [01](01-accounting-foundation.md) poin 51 (sub-kategori tiap tipe akun) khusus utk siklus Pembelian.

### E. Penjualan — mirror poin D, arah dibalik (2026-08-26)

**1 asimetri penting** (bukan cuma "kebalik doang"): Pembelian punya akun perantara **Hutang Belum Difaktur** (GRNI) krn barang diterima duluan sebelum ada kewajiban resmi. Penjualan **tidak punya akun perantara serupa** ("Piutang Belum Difaktur") — begitu barang dikirim, yang diakui langsung **Beban Pokok Penjualan (HPP)** sebagai beban (bukan piutang), krn piutang/pendapatan baru boleh diakui pas invoice terbit (prinsip pengakuan pendapatan), sedangkan HPP diakui pas barang keluar gudang (matching cost dgn keluarnya barang, terlepas dari kapan ditagih).

0. **Sales Order (SO) — ringan** (mirror PO ringan, poin D poin 0): header `partner_id` (customer, wajib), tanggal, `cost_center_id`, keterangan. `line_ids`: `product_id`, qty, harga jual satuan → subtotal (sama, tanpa UoM). State `draft`→`confirmed`. Modul tetap `c18_account`, nanti `_inherit` oleh `c18_sale` (Standard). Wajib jadi referensi Uang Muka Penjualan (poin 3); opsional buat Pengiriman Barang/Penjualan.
1. **Pengiriman Barang** — referensi `so_ref_id` (mendukung pengiriman sebagian per baris). Akun **fixed**: debit **Beban Pokok Penjualan** (akun baru tipe "Beban Pokok Pendapatan"), kredit **Persediaan**. Cuma relevan utk produk tipe **Barang Stok** — Jasa/Barang Non Stok tidak lewat dokumen ini sama sekali (langsung ke Penjualan tanpa entry Persediaan/HPP).
2. **Penjualan** (invoice customer) — debit **Piutang Usaha** (fixed). Kredit akun pendapatan **bebas dipilih user** (mirror Pembelian: kredit Hutang Usaha ↔ debit Piutang Usaha; debit bebas Beban/Persediaan ↔ kredit bebas Pendapatan).
   - `line_ids`: `product_id` (opsional) + keterangan + qty + harga → subtotal, sama pola Pembelian (poin D poin 2) — auto-fill dari `so_ref_id`/`delivery_ref_id` kalau diisi, tetap editable.
   - **Referensi `delivery_ref_id` (opsional, Many2one ke Pengiriman Barang)** — beda peran dari `grni_ref_id` di Pembelian (yang nentuin akun debit): di sini cuma buat auto-fill line & audit trail, **tidak** mengubah akun (kredit Pendapatan tetap sama ada/tidaknya referensi ini) — konsekuensi dari asimetri di atas.
   - **Kalau `delivery_ref_id` kosong DAN ada baris `product_id` bertipe Barang Stok** (brg belum pernah dikirim lewat dokumen terpisah) — sistem generate **2 pasang jurnal sekaligus** dalam 1 dokumen: (a) debit Piutang Usaha / kredit Pendapatan (revenue), **dan** (b) debit HPP / kredit Persediaan (COGS, persis seperti poin 1) — supaya Persediaan tetap ke-track walau invoice langsung tanpa Pengiriman Barang terpisah.
   - Baris `product_id` bertipe Jasa/Barang Non Stok — cuma (a), tidak ada (b).
3. **Uang Muka Penjualan** — **wajib** referensi `so_ref_id`. Debit `account_id` **Kas/Bank** (dipilih user), kredit **Uang Muka Penjualan** (fixed, akun baru tipe **"Hutang Lancar Lainnya"** — beda dari Uang Muka Pembelian yang tipe Aktiva Lancar Lainnya, krn ini kewajiban kita ke customer, bukan aktiva kita).
4. **Penerimaan Piutang** (mirror Pembayaran Vendor) — kredit **Piutang Usaha** (fixed, per baris invoice), debit `account_id` (header) — **dilonggarkan sama seperti poin 4 Pembelian**: default Kas/Bank, tapi boleh akun lain buat pelunasan non-kas (Hutang Usaha utk netting kalau customer itu juga vendor kita, Persediaan kalau customer bayar pakai barang/barter, **atau Uang Muka Penjualan (poin 3) buat nge-apply/netting uang muka ke invoice akhir** — sama mekanismenya dg Uang Muka Pembelian).
   - `line_ids`: `invoice_id` (Many2one ke Penjualan outstanding), nilai tagihan awal, nilai tagihan sisa, nominal terima, deduction (1 kolom, wizard sama persis pola Pembelian).
   - **Arah deduction dibalik**: positif (pengurang, mis. potongan tunai/cash discount ke customer) → **debit** akun tsb (mis. Beban/Potongan Penjualan — kita yang rugi, bukan untung); negatif (penambah, mis. denda keterlambatan) → **kredit** akun tsb (mis. Pendapatan Denda).
5. **Retur Barang Customer** (mirror Retur Barang Vendor) — kredit sisi tergantung tahap dokumen sumbernya, debit **Persediaan** (fixed, barang balik masuk gudang) — mirip Pembelian tapi lebih banyak kombinasi krn ada 2 leg yang mungkin perlu dibalik terpisah:
   - **Baru sampai Pengiriman Barang, belum invoice** — reverse cuma leg HPP/Persediaan: debit Persediaan, kredit **HPP** (membatalkan beban pokok yang sudah diakui).
   - **Sudah invoice** — reverse leg revenue juga: kredit **Piutang Usaha** (piutang berkurang), debit akun kontra-revenue **"Retur & Potongan Penjualan"** (bukan debit langsung ke akun Pendapatan asli — praktik umum, supaya Pendapatan kotor & Retur kelihatan terpisah di Laporan Laba Rugi) — plus tetap leg Persediaan/HPP kalau produknya Barang Stok.
   - **Sudah invoice DAN sudah diterima pembayarannya (sebagian/lunas)** — sama seperti Pembelian: retur tetap jalan normal (kredit Piutang Usaha), walau saldo piutang invoice itu jadi **negatif** (customer overpaid) — diselesaikan lewat **Penerimaan Piutang (poin 4) yang sama**, nominal terima **negatif** (refund keluar ke customer).
6. **Write-off Piutang** (mirror Write-off Hutang, tapi arahnya kerugian bukan untung) — debit **Beban Piutang Tak Tertagih** (fixed, akun baru tipe "Beban Usaha" — piutang yang tidak tertagih itu **kerugian**, kebalikan dari Write-off Hutang yang untung), kredit **Piutang Usaha** (fixed, piutang dihapuskan). Scope & kriteria ">360 hari" sama persis logikanya dengan poin 6 Pembelian (cuma pemicu, bukan mekanisme beda) — dan ini **cocok** dengan hasil riset awal soal PMK 207/PMK.010/2015 (piutang tak tertagih bisa jadi pengurang penghasilan bruto/deductible, kalau syaratnya terpenuhi) yang sempat kelewat relevan pas dibahas di sisi Hutang.

Akun-akun baru yang perlu ditambah ke data default CoA: **Uang Muka Penjualan** (tipe Hutang Lancar Lainnya), **Beban Pokok Penjualan/HPP** (tipe Beban Pokok Pendapatan), **Retur & Potongan Penjualan** (kontra-revenue, tipe Pendapatan — biasanya presented sbg pengurang di Laporan Laba Rugi), **Beban Piutang Tak Tertagih** (tipe Beban Usaha).

### F. Persediaan — mekanisme costing FIFO/Average (2026-08-26, melengkapi gap "Belum Diputuskan" sebelumnya)

**Metode dipilih per company** (dikonfirmasi 2026-08-26) — 1 field `costing_method` (selection: FIFO / Average) di Settings company, berlaku **sama ke semua produk** tipe Barang Stok (bukan per produk — biar konsisten dgn semangat Basic yang sederhana). LIFO sengaja tidak disediakan (tidak direkomendasikan PSAK).

**Penyimpanan** — beda struktur tergantung metode, krn kebutuhan datanya beda:
- **FIFO** — butuh tabel layer terpisah `c18.account.stock.layer`: `product_id`, tanggal (urutan konsumsi), qty asal, **qty sisa** (berkurang tiap konsumsi), harga satuan (dari baris dokumen sumber), referensi sumber (Penerimaan Barang / Retur Customer yang menambah layer ini).
- **Average** — **tidak perlu** tabel layer, cukup 2 field running di `c18.product`: `qty_on_hand` (total qty tersedia) dan `avg_cost` (harga rata-rata berjalan per unit), di-update tiap mutasi.

**Efek tiap mutasi ke Persediaan** (murni mekanisme stok/costing — jurnalnya sudah dirinci di poin D/E, di sini fokus ke bagaimana nilainya dihitung):
1. **Penerimaan Barang** (poin D poin 1) — stok **nambah**. FIFO: bikin layer baru (qty asal = qty sisa = qty diterima, harga = harga satuan baris PO/GR). Average: `qty_on_hand += qty`, `avg_cost` dihitung ulang **weighted average** = (nilai lama + qty×harga baru) ÷ qty_on_hand baru.
2. **Pengiriman Barang / Penjualan langsung produk Barang Stok** (poin E poin 1/2) — stok **berkurang**, ini yang menentukan nilai HPP di jurnal. FIFO: konsumsi dari layer **paling lama** dulu (kurangi qty sisa; kalau qty keluar > 1 layer, HPP jadi gabungan dari beberapa layer sekaligus/split). Average: HPP = qty keluar × `avg_cost` saat itu (avg_cost sendiri tidak berubah krn barang keluar, cuma qty_on_hand berkurang).
3. **Retur Barang Vendor** (poin D poin 5) — stok **berkurang** (barang balik ke vendor). FIFO: kurangi dari layer yang sama kalau referensinya jelas (match ke Penerimaan Barang asal via `grni_ref_id`/`po_ref_id`); kalau tidak match jelas, default ambil dari layer terbaru (asumsi retur biasanya cepat setelah terima). Average: `qty_on_hand` berkurang, nilai keluar = qty × `avg_cost` saat itu.
4. **Retur Barang Customer** (poin E poin 5) — stok **nambah balik**. FIFO: bikin layer baru dengan harga = **harga HPP yang dulu dipakai** waktu Pengiriman Barang asal (bukan harga pasar baru — supaya reversal jurnalnya presisi/simetris). Average: `qty_on_hand += qty`, nilai yang masuk = nilai HPP asal juga (bukan `avg_cost` saat ini), lalu `avg_cost` dihitung ulang dari situ.
5. **Pemakaian Sendiri (Consume)** — lihat jenis jurnal baru di bawah — stok **berkurang**, perlakuan sama seperti poin 2 (konsumsi FIFO dari layer terlama / Average pakai `avg_cost` saat itu), bedanya nilai keluar ini jadi **Beban** (bukan HPP, krn bukan bagian penjualan).

**Stok negatif: tidak diperbolehkan** (dikonfirmasi 2026-08-26, koreksi dari "belum diputuskan" sebelumnya) — semua mutasi keluar (Pengiriman Barang, Penjualan langsung, Retur Vendor, Pemakaian Sendiri) **wajib divalidasi** dulu terhadap `qty_on_hand`/total qty sisa layer sebelum diizinkan posting; kalau qty keluar > stok tersedia, **ditolak** (bukan cuma warning).

**Laporan (diriset 2026-08-26, scope Basic dikonfirmasi — [kledo.com](https://kledo.com/blog/kartu-stok-barang/), [jurnal.id](https://www.jurnal.id/id/blog/kartu-stok-barang-adalah/), [help.accurate.id](https://help.accurate.id/product/accurate-online/fitur-aol/persediaan/perintah-stok-opname/mengenal-fitur-perintah-stok-opname/))**:
- **Kartu Stok per produk** — mutasi kronologis (tanggal, jenis transaksi/referensi, qty masuk/keluar, saldo qty berjalan, harga pokok saat itu, nilai). **Layout dirinci (2026-08-26)**:
  - **Filter/header laporan**: `product_id` (wajib, 1 kartu = 1 produk), rentang tanggal, opsional filter `cost_center_id`.
  - **Kolom per baris mutasi** (urut kronologis by tanggal + jam input, saldo berjalan naik-turun tiap baris):

    | Tanggal | No. Dokumen | Jenis Transaksi | Qty Masuk | Qty Keluar | Saldo Qty | Harga Pokok/Unit | Nilai Masuk | Nilai Keluar | Saldo Nilai |
    |---|---|---|---|---|---|---|---|---|---|
    | 05/08/2026 | PNBR-2026-08-001 | Penerimaan Barang | 100 | — | 100 | 15.000 | 1.500.000 | — | 1.500.000 |
    | 10/08/2026 | PNGB-2026-08-004 | Pengiriman Barang | — | 30 | 70 | 15.000 | — | 450.000 | 1.050.000 |
    | 18/08/2026 | RTBC-2026-08-002 | Retur Barang Customer | 5 | — | 75 | 15.000 | 75.000 | — | 1.125.000 |
    | 25/08/2026 | SOPN-2026-08-001 | Stok Opname (selisih -2) | — | 2 | 73 | 15.000 | — | 30.000 | 1.095.000 |

  - **Baris saldo awal** (di atas baris pertama tiap rentang tanggal yang difilter) — qty & nilai saldo awal periode, supaya laporan tetap benar walau di-filter parsial (bukan dari awal berdirinya produk).
  - `No. Dokumen` klik-through ke record sumbernya (drill-down, sesuai prinsip generic reference [01](01-accounting-foundation.md) poin 3).
  - **FIFO**: "Harga Pokok/Unit" bisa beda-beda per baris keluar kalau melewati batas antar-layer (baris keluar itu di-split jadi beberapa baris kartu stok, 1 baris per layer yang dikonsumsi). **Average**: selalu 1 angka per baris (avg_cost saat itu).
- **Saldo Persediaan** — ringkasan qty on hand + nilai per produk saat ini; total harus cocok ke saldo akun Persediaan di Neraca. Ini tujuan awal fitur poin F ("saldo persediaan dirinci per produk").
- **Kartu Stok per Gudang** — tidak masuk scope Basic (butuh multi-warehouse, itu Standard+/[03-inventory-foundation.md](03-inventory-foundation.md)).
- **Laporan Stok Minimum** — **dikonfirmasi tidak perlu** (bukan cuma ditunda) — tidak ada rencana field/mekanisme reorder-alert di MVP ini sama sekali.

### F.1 Pemakaian Sendiri (Consume) — jenis jurnal baru (2026-08-26)
Bukan bagian 6 jenis Pembelian/Penjualan resmi dari `tiering-versi.txt` — tambahan yang diidentifikasi belakangan: barang keluar dari Persediaan **bukan** karena dijual ke customer atau diretur ke vendor, tapi **dipakai sendiri secara internal** (mis. ATK kantor, sample/QC, bahan baku dipakai buat kebutuhan internal non-jual).
- **Field**: tanggal, `product_id` (wajib, harus tipe Barang Stok — kalau bukan Barang Stok tidak relevan, tidak ada Persediaan yang dikurangi), qty, keterangan (tujuan pemakaian), `cost_center_id` (opsional, relevan buat tracking pemakaian per departemen).
- **Akun**: kredit **Persediaan** (fixed, barang keluar/berkurang), debit **bebas dipilih user** (akun Beban apa saja sesuai tujuan — Beban ATK, Beban Operasional, dll — pola sama seperti debit bebas di Pembelian poin D poin 2).
- **State**: `draft` → `posted` (langsung jurnal, sesuai konvensi dokumen yang menghasilkan jurnal).
- Modul: tetap bagian `c18_account` (sejalan dgn keputusan PO/Product tetap di situ), pakai form generik yang sama (poin D).

### F.2 Stok Opname (Penyesuaian Persediaan) — jenis jurnal baru (2026-08-26)
Juga bukan bagian 6 jenis resmi `tiering-versi.txt` — tapi penting secara praktis krn stok fisik vs stok sistem pasti pernah beda (rusak, hilang, salah catat, dll), dan `qty_on_hand`/layer FIFO (poin F) butuh cara buat dikoreksi manual.
- **Field**: tanggal, `product_id` (wajib, Barang Stok), **qty sistem** (readonly, dari `qty_on_hand`/total qty sisa layer saat itu), **qty fisik** (input user, hasil hitung fisik), **selisih** (computed = qty fisik − qty sistem), keterangan (alasan selisih), `cost_center_id` (opsional).
- **Akun** — **fixed kedua sisi** (beda dari Pemakaian Sendiri yang debitnya bebas — ini murni administratif/koreksi, bukan transaksi bisnis pilihan bebas), pakai 1 akun baru **"Selisih Persediaan"** (tipe Beban Usaha kalau sering minus, tapi disediakan 1 akun yang bisa didebit/dikredit tergantung arah):
  - **Selisih negatif** (fisik < sistem, kekurangan/kehilangan): debit **Selisih Persediaan**, kredit **Persediaan**.
  - **Selisih positif** (fisik > sistem, kelebihan): debit **Persediaan**, kredit **Selisih Persediaan**.
- **Efek ke costing (poin F)**: selisih negatif → konsumsi FIFO dari layer terlama (atau kurangi qty_on_hand di Average) sejumlah selisih, sama pola Pemakaian Sendiri. Selisih positif → FIFO bikin layer baru dgn harga = harga layer terakhir yang pernah dipakai (atau `avg_cost` saat ini kalau Average) sbg estimasi, krn tidak ada dokumen sumber pasti.
- **State**: `draft` → `posted`.
- Modul: tetap `c18_account`, form generik sama (poin D).

### G. Aktiva Tetap Basic — **tanpa register aset**, murni jurnal
**Tidak ada** model/daftar aset (`asset_id`, kode aset, kategori, dst) di tier Basic — kalau disediakan UI "Daftar Aktiva Tetap" tapi nilainya cuma angka manual tanpa kalkulasi penyusutan otomatis, itu kesan fitur setengah jadi yang bakal menimbulkan pertanyaan klien ("kok nanggung"). Register aset (dengan kategori, umur ekonomis, kalkulasi otomatis) baru mulai dibangun di **Standard**, sebagai model baru, bukan upgrade dari sesuatu yang sudah ada.

Basic cukup pakai **form generik yang sama seperti poin D** (1 form, bukan 5 form terpisah) — bedanya cuma di header ada field pilih **tipe transaksi aktiva tetap** (selection: Pengakuan / Penyusutan / Penghapusan / Penjualan / Revaluasi), yang menentukan `journal_id` dipakai (5 jenis jurnal Aktiva Tetap tetap ada sebagai master jurnal, sesuai [01-accounting-foundation.md](01-accounting-foundation.md) poin 2 — cuma bedanya di sini dipilih di 1 form, bukan 5 menu/form terpisah, beda dari poin D yang tiap jenis dapat menu sendiri). User input akun & jumlah manual sendiri per transaksi (tidak ada kalkulasi/asset tracking apapun).

### H. Payroll Basic — 2 jenis jurnal
Sama pola form generik seperti poin D (1 template, header pilih akun/partner/cost center/jumlah), tapi arah debit/kredit-nya **sudah pasti** (bukan generic bebas):
- **Jurnal Pengakuan (Hutang Gaji)**: debit Beban Gaji, kredit Hutang Gaji.
- **Jurnal Pembayaran (Bayar Gaji)**: debit Hutang Gaji, kredit Kas/Bank — alurnya mirip Kas Keluar (poin B), tapi sengaja dipisah jadi jenis jurnal sendiri (bukan numpang form Kas Keluar) supaya tetap kelacak sebagai transaksi Payroll, bukan Kas Bank umum.

**Rincian relasi Pengakuan ↔ Pembayaran (2026-08-26)** — mirror pola `bill_id`/"Buat Tagihan" di Pembelian (poin D poin 2/4), 2 cara akses:
- **Pull (dari form Jurnal Pembayaran)**: `line_ids` — pilih `pengakuan_id` (Many2one ke record Jurnal Pengakuan, **filter cuma yang saldo Hutang Gaji-nya masih > 0**, alias belum lunas), **nilai hutang awal** (readonly), **nilai hutang sisa** (readonly), **nominal bayar** (input user, ≤ nilai hutang sisa). Sama struktur dengan `line_ids` Pembayaran Vendor (poin D poin 4), tanpa deduction dulu (belum diminta, bisa nyusul pola yang sama kalau nanti perlu potongan kayak PPh 21/BPJS/kasbon).
- **Push (dari form Jurnal Pengakuan)**: tombol **"Bayar"** — bikin record Jurnal Pembayaran baru dengan `line_ids` sudah ke-prefill (`pengakuan_id` = record ini, nominal bayar = sisa hutang penuh), tinggal user koreksi/simpan. Shortcut ke mekanisme yang sama, bukan alur terpisah — persis pola tombol "Buat Tagihan" di Penerimaan Barang.

### I. Partner Basic — field minimal
Tidak perlu model/view terpisah dari Standard — cukup pastikan field yang ditonjolkan di form Basic dibatasi ke: nama, `is_customer`/`is_vendor`, NPWP, termin pembayaran default, alamat tunggal (bukan multi-alamat tagih/kirim — itu baru relevan pas ada Delivery di Standard). Field logistik (kontak PIC banyak, alamat kirim terpisah, dst) tidak perlu ditampilkan tapi tidak perlu dihapus dari `res.partner` (tetap ada by default, cuma tidak ditonjolkan di view Basic).

### J. Product/UoM di Basic (dikoreksi 2026-08-26)
- **Product**: **dipakai**, bukan "tidak sama sekali" seperti draft awal — PO ringan (poin D poin 0) referensi `product_id` ke `c18.product` versi sederhana (kode dg konvensi prefix, nama, tipe, `is_purchaseable`/`is_saleable` — tanpa kategori model & tanpa UoM), lihat [02-common-master-data.md](02-common-master-data.md).
- **UoM**: **tetap tidak dipakai** di Basic — qty di baris PO/Penerimaan Barang polos tanpa satuan/konversi. Dependency ke `c18.uom.uom` baru muncul mulai `c18_purchase`/`c18_sale`/`c18_stock` (Standard), yang `_inherit` `c18.product` buat nambah `uom_id`.

### K. Skema Nomor Dokumen (2026-08-26, dikonfirmasi)
Placeholder `ir.sequence` sudah dibuat di [`app/mvp/c18_account/data/ir_sequence_data.xml`](../../app/mvp/c18_account/data/ir_sequence_data.xml), siap dipakai begitu module `c18_account` mulai discaffold.

**Format tampilan**: `KODE-yyyy-mm-xxx` (`yyyy`/`mm` cuma menunjukkan tanggal transaksi berjalan saat itu, `xxx` = 3 digit). **Nomor urut (`xxx`) berlanjut terus tanpa reset** (bukan reset tiap bulan/tahun) — dikonfirmasi 2026-08-26, sesuai semangat Basic yang sederhana. Teknis: `ir.sequence` dipakai **tanpa** `use_date_range` (counter tunggal global per jenis jurnal, `%(year)s`/`%(month)s` di prefix cuma menampilkan tanggal berjalan, tidak memicu reset counter). **Kode prefix maks 4 huruf** (dikonfirmasi 2026-08-26). Daftar kode per jenis jurnal (ditentukan sendiri, belum dikonfirmasi user — cek ulang pas review):

| Kode | Jenis Jurnal | Poin |
|---|---|---|
| JU | Jurnal Umum | A |
| PAWL | Penyesuaian Awal Tahun | C |
| PAKH | Penyesuaian Akhir Tahun | C |
| TUTB | Tutup Buku | C |
| KM | Kas Masuk | B |
| KK | Kas Keluar | B |
| TRF | Transfer Kas/Bank | B |
| PO | Purchase Order (ringan) | D.0 |
| PNBR | Penerimaan Barang | D.1 |
| PB | Pembelian (Vendor Bill) | D.2 |
| UMPB | Uang Muka Pembelian | D.3 |
| BPV | Pembayaran Vendor | D.4 |
| RTBV | Retur Barang Vendor | D.5 |
| WOHT | Write-off Hutang | D.6 |
| SO | Sales Order (ringan) | E.0 |
| PNGB | Pengiriman Barang | E.1 |
| PJ | Penjualan (Customer Invoice) | E.2 |
| UMPJ | Uang Muka Penjualan | E.3 |
| BPP | Penerimaan Piutang | E.4 |
| RTBC | Retur Barang Customer | E.5 |
| WOPT | Write-off Piutang | E.6 |
| PMKS | Pemakaian Sendiri (Consume) | F.1 |
| SOPN | Stok Opname | F.2 |
| AKAT / PNYT / HAPS / JLAT / RVLS | Aktiva Tetap — Pengakuan/Penyusutan/Penghapusan/Penjualan/Revaluasi | G |
| HGJ | Payroll — Jurnal Pengakuan (Hutang Gaji) | H |
| BGJ | Payroll — Jurnal Pembayaran (Bayar Gaji) | H |

Semua pakai `implementation="no_gap"` (penomoran tanpa celah, sesuai kebutuhan audit dokumen akuntansi) — ini asumsi saya, belum dikonfirmasi eksplisit, tandai kalau mau diganti `standard` (boleh ada celah, lebih cepat/tidak lock row).

## Ditunda ke Tier Enterprise (Bukan Bagian MVP)
- **Bank Reconciliation**.
- **Budget**.
