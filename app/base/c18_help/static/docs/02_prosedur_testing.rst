Prosedur Testing Manual - c18_basic_erp (Skenario PT Roda Sejahtera)
====================================================================

Dokumen ini untuk tester yang **tidak punya background akuntansi**.
Ikuti 1 cerita utuh: perusahaan distributor ban **PT Roda Sejahtera**,
berdiri November 2024, datanya sudah lengkap disiapkan di
01-transaksi-distributor-ban.md
(baca
00-skenario-distributor-ban.md dulu
kalau mau tahu latar belakang perusahaannya).

Status: draft awal (2026-08-27, ditambah gap-coverage 2026-08-28), belum
pernah dijalankan tester sungguhan.

**Cara pakai 2 dokumen ini bareng**: dokumen **01** isinya tabel
tanggal+nominal (data mentah, urut kronologis). Dokumen **ini (02)**
isinya cara menginput tiap jenis dokumen ke sistem (menu, field mana
diisi apa). Kerjakan tabel di 01 **baris demi baris sesuai tanggal**,
sambil rujuk bagian “Cara Input” di bawah sesuai jenis dokumennya.

Istilah Dasar (sekali baca cukup)
---------------------------------

+-----------------------------------+-----------------------------------+
| Istilah                           | Artinya (versi awam)              |
+===================================+===================================+
| **Kas/Bank**                      | Uang tunai atau saldo rekening    |
|                                   | bank perusahaan.                  |
+-----------------------------------+-----------------------------------+
| **Piutang**                       | Uang yang **akan diterima** dari  |
|                                   | customer (customer belum bayar).  |
+-----------------------------------+-----------------------------------+
| **Hutang**                        | Uang yang **harus dibayar** ke    |
|                                   | vendor (kita belum bayar).        |
+-----------------------------------+-----------------------------------+
| **Persediaan**                    | Nilai barang yang masih ada di    |
|                                   | gudang (belum terjual).           |
+-----------------------------------+-----------------------------------+
| **HPP (Harga Pokok Penjualan)**   | Modal/biaya dari barang yang      |
|                                   | sudah terjual (bukan harga        |
|                                   | jualnya).                         |
+-----------------------------------+-----------------------------------+
| **Jurnal / Posting**              | Transaksi yang disimpan permanen. |
|                                   | Sebelum “Post”/“Confirm”          |
|                                   | statusnya Draft (masih bisa       |
|                                   | diedit/dihapus), sesudah jadi     |
|                                   | Posted/Confirmed (permanen).      |
+-----------------------------------+-----------------------------------+
| **FIFO (First In First Out)**     | Barang yang dibeli **duluan**     |
|                                   | dianggap keluar/terjual           |
|                                   | **duluan** juga — kalau ada 2x    |
|                                   | beli dengan harga beda, sistem    |
|                                   | otomatis pakai harga beli yang    |
|                                   | lebih lama dulu.                  |
+-----------------------------------+-----------------------------------+

Cara Akses Aplikasi
-------------------

1. Terminal → folder ``app/docker/`` →
   ``docker compose up -d db odoo18-erp``.
2. Tunggu ±10 detik, buka ``http://localhost:8069/odoo``.
3. Pilih/buat database **testing terpisah** (jangan pakai database kerja
   utama).
4. Login admin. Menu ada di **ERP > Accounting**.
5. Sebelum mulai, pastikan Settings > General Settings > Companies >
   **Costing Method = FIFO** (skenario ini pakai FIFO sepanjang cerita).

**Format laporan bug**: Tanggal/baris di tabel 01 yang gagal → Langkah
mana → Yang diharapkan → Yang terjadi → Screenshot.

--------------

Bagian 0 — Setup Data Master (sekali di awal)
---------------------------------------------

1. Buat 1 vendor: **PT Ban Nusantara Distribusi** (contact baru, centang
   Vendor).
2. Buat 4 customer: **Toko Ban Makmur**, **UD Roda Mas**, **Bengkel
   Sinar Jaya**, **Toko Onderdil Abadi** (centang Customer).
3. Buat 9 produk sesuai tabel Master Produk di
   `00-skenario-distributor-ban.md <00-skenario-distributor-ban.md#d-master-produk---9-sku-ban>`__
   — Tipe = Barang Stok, Bisa Dibeli & Bisa Dijual = Ya.
4. Cek Chart of Accounts sudah ada **42 akun** bawaan, termasuk “6-1600
   Beban Sewa” (akun baru ditambah 2026-08-28) — tidak perlu tambah akun
   manual.
5. Buat 2 Cost Center (ERP > Accounting > Konfigurasi > Cost Center):
   **Operasional** dan **Gudang** — dipakai buat nge-tag sebagian
   transaksi batch Maret 2026 (opsional untuk bulan-bulan lain, boleh
   dikosongkan).

--------------

Cara Input Tiap Jenis Dokumen
-----------------------------

Bagian ini dirujuk berulang-ulang saat mengerjakan tabel di 01 — tidak
perlu dibaca urut, cukup cari sub-bagian sesuai kolom “Dokumen” di tabel
01.

Modal Saham
~~~~~~~~~~~

Pakai **Kas Masuk** (ERP > Accounting > Kas Bank > Kas Masuk): Akun
Kas/Bank = “1-1100 Bank”, baris akun lawan = “3-1000 Modal”, nominal
sesuai tabel.

Sewa Kantor (pembayaran lunas dimuka, Tahun 1 & Tahun 2)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pakai **Jurnal Umum** (bukan Kas Keluar, karena melibatkan akun “Biaya
Dibayar Dimuka” yang bukan sekadar 1 akun lawan): baris 1 = Debit
“1-1420 Biaya Dibayar Dimuka” sejumlah nominal; baris 2 = Kredit “1-1100
Bank” sejumlah sama. Post.

Amortisasi Sewa (bulanan)
~~~~~~~~~~~~~~~~~~~~~~~~~

Pakai **Jurnal Umum**: baris 1 = Debit **“6-1600 Beban Sewa”** Rp
10.000.000; baris 2 = Kredit “1-1420 Biaya Dibayar Dimuka” Rp
10.000.000. Keterangan = “Amortisasi sewa kantor bulan X”. Post. Ulangi
tiap bulan sesuai tabel 01 (tidak jalan waktu sewa tahun 1 sudah habis &
sewa tahun 2 belum mulai - lihat catatan di tabel September 2025).

Aktiva Tetap (semua jenis - Pengakuan/Penyusutan/Penghapusan/Penjualan/Revaluasi)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**ERP > Accounting > Aktiva Tetap**, New. Pilih “Jenis Transaksi” sesuai
tabel, isi Akun Debit & Akun Kredit & Jumlah sesuai tabel (kolom “Jenis
Transaksi”/“Akun Debit”/“Akun Kredit” ada di tabel G.5 dokumen 01 untuk
4 jenis terakhir; untuk “Pengakuan” perabotan kantor di November 2024,
Akun Debit = “1-2300 Peralatan Kantor”, Akun Kredit = “1-1100 Bank”).
Post. Semua jenis pakai form & model yang sama, cuma beda pilihan
dropdown.

Kas Keluar (ATK, Listrik, Internet)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**ERP > Accounting > Kas Bank > Kas Keluar**. Akun Kas/Bank sesuai kolom
“Bayar” di tabel (Kas/Bank). Kalau ada 2 komponen (mis. Listrik +
Internet), buat 2 baris akun lawan dalam 1 dokumen yang sama (semua ke
“6-1200 Beban Operasional” kecuali disebut lain). Post.

PO → Penerimaan Barang → Buat Tagihan → Pembayaran Vendor
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ini **1 alur 4 langkah** untuk tiap baris pembelian di tabel 01: 1.
**ERP > Accounting > Pembelian > Purchase Order**, New. Vendor = “PT Ban
Nusantara Distribusi”, isi baris produk+qty+harga sesuai tabel.
**Confirm**. 2. **Penerimaan Barang**, New, pilih PO tadi (baris
otomatis terisi). **Post**. → cek stok produk terkait bertambah sesuai
qty. 3. Buka lagi dokumen Penerimaan Barang, klik tombol **“Buat
Tagihan”** → otomatis buka Pembelian baru dengan baris terisi. 4. Di
Pembelian itu, **Post**. 5. **ERP > Accounting > Pembelian > Pembayaran
Vendor**, New. Vendor sama, Akun Kredit = “1-1100 Bank” (atau “1-1000
Kas” kalau tabel bilang Kas). Baris invoice pilih Pembelian dari langkah
4, Nominal Bayar = full (lunas). **Post**.

SO → Delivery → Invoice → Pembayaran
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alur mirror untuk tiap baris penjualan: 1. **ERP > Accounting >
Penjualan > Sales Order**, New. Customer sesuai tabel, isi baris
produk+qty+harga jual. **Confirm**. 2. **Pengiriman Barang**, New, pilih
SO tadi. **Post**. → cek stok berkurang & muncul “Total HPP”. 3.
**Penjualan**, New. Customer sama, pilih “Pengiriman Barang” = dokumen
langkah 2. Akun Pendapatan = “4-1000 Pendapatan Penjualan/Jasa”. Isi
baris produk+qty+harga sama seperti SO. **Post**. 4. **Kalau kolom
“Bayar” di tabel = Kas/Bank (lunas hari itu)**: lanjut buat **Penerimaan
Piutang** (ERP > Accounting > Penjualan > Penerimaan Piutang), Akun
Debit sesuai (Kas/Bank), baris invoice pilih Penjualan langkah 3,
Nominal Terima = full. **Post**. 5. **Kalau kolom “Bayar” di tabel =
“Piutang”**: **skip langkah 4 untuk sekarang** — nanti dilunasi di
tanggal yang disebutkan di tabel (lihat sub-bagian “Penerimaan Piutang”
di bawah).

Penerimaan Piutang (pelunasan piutang yang tertunda)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sama seperti langkah 4 di atas, tapi dieksekusi di tanggal pelunasan
(bukan tanggal invoice). **Kalau tabel menyebut “dengan
potongan/deduction”**: setelah isi baris invoice & Nominal Terima,
scroll ke bagian bawah “Deduction”, tambah 1 baris: Keterangan bebas,
Akun bebas (boleh pakai “8-1000 Pendapatan Lain-lain” kalau belum ada
akun spesifik), Nominal = sesuai tabel (positif). Post.

Retur Barang Customer (sudah invoice)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**ERP > Accounting > Penjualan > Retur Barang Customer**, New. Pilih
“Penjualan (sudah invoice)” = invoice terkait. Isi baris produk+qty yang
diretur, Harga Jual Satuan sesuai harga invoice asal. **Post**. → cek
stok produk itu **bertambah** lagi. Kalau tabel bilang “Refund via
Penerimaan Piutang nominal negatif”: buat Penerimaan Piutang baru, pilih
invoice yang sama, isi **Nominal Terima dengan angka MINUS** (mis.
-1.900.000) untuk uang yang dikembalikan ke customer.

Write-off Piutang
~~~~~~~~~~~~~~~~~

**ERP > Accounting > Penjualan > Write-off Piutang**, New. Pilih
Penjualan yang mau dihapuskan, Jumlah otomatis terisi sisa piutangnya.
**Post**.

Uang Muka Pembelian
~~~~~~~~~~~~~~~~~~~

**ERP > Accounting > Pembelian > Uang Muka Pembelian**, New. Pilih PO
(wajib sudah Confirm), Akun Kas/Bank sesuai tabel, Jumlah sesuai tabel.
**Post**. Ini transaksi berdiri sendiri (bukan bagian alur PO→Penerimaan
Barang→dst) - PO-nya tetap lanjut diproses normal lewat alur biasa
setelahnya.

Apply DP ke Pembayaran Vendor/Penerimaan Piutang (netting Uang Muka ke tagihan akhir)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Begitu tagihan (Pembelian/Penjualan) akhir sudah terbit, alokasikan Uang
Muka yang sudah dibayar/diterima sebelumnya dengan bikin **Pembayaran
Vendor** (atau **Penerimaan Piutang**) terpisah, tapi Akun Kredit-nya
(Pembayaran Vendor) atau Akun Debit-nya (Penerimaan Piutang) diisi
**“1-1400 Uang Muka Pembelian”** (atau **“2-1200 Uang Muka Penjualan”**)
- bukan Kas/Bank. Nominal = sebesar DP yang mau di-apply. Sisa tagihan
yang belum ke-cover DP, baru dibikinkan 1 dokumen Pembayaran/Penerimaan
lagi dengan Akun Kas/Bank seperti biasa.

Retur Barang Vendor
~~~~~~~~~~~~~~~~~~~

**ERP > Accounting > Pembelian > Retur Barang Vendor**, New. Kalau tabel
bilang “sudah invoice”: pilih field “Pembelian (sesudah invoice)” = Bill
terkait. Kalau “sebelum invoice”: pilih field “Penerimaan Barang
(sebelum invoice)”. Isi baris produk+qty yang diretur. **Post**. → cek
stok produk itu **berkurang**. Kalau tagihan itu **sudah lunas duluan**,
saldo tagihannya bakal jadi **negatif** (vendor “berhutang balik”) -
selesaikan dengan bikin **Pembayaran Vendor** baru, pilih Bill yang
sama, isi **Nominal Bayar dengan angka MINUS** (refund, uang masuk balik
dari vendor).

Write-off Hutang
~~~~~~~~~~~~~~~~

**ERP > Accounting > Pembelian > Write-off Hutang**, New. Pilih
Pembelian yang mau dihapuskan, Jumlah otomatis terisi sisa tagihannya.
**Post**.

Pemakaian Sendiri
~~~~~~~~~~~~~~~~~

**ERP > Accounting > Persediaan > Pemakaian Sendiri**, New. Product
sesuai tabel, Qty sesuai tabel, Akun Beban bebas (isi sesuai tabel kalau
disebutkan, kalau tidak pakai “6-1200 Beban Operasional”), Cost Center
kalau disebutkan di tabel. **Post**. → cek stok produk itu
**berkurang**.

Stok Opname
~~~~~~~~~~~

**ERP > Accounting > Persediaan > Stok Opname**, New. Pilih Product -
field “Qty Sistem” otomatis muncul (readonly, dari stok saat ini). Isi
“Qty Fisik” sesuai instruksi tabel (mis. “sistem −1” berarti kalau Qty
Sistem = 9, isi Qty Fisik = 8). Cost Center kalau disebutkan. **Post**.
→ field “Difference” & “Amount” muncul otomatis, stok produk ikut
menyesuaikan ke Qty Fisik yang diinput.

Payroll
~~~~~~~

1. **ERP > Accounting > Payroll > Jurnal Pengakuan (Hutang Gaji)**, New.
   Jumlah = total gaji bulan itu (sesuai tabel), Keterangan = “Gaji
   bulan X tahun Y”, Cost Center kalau disebutkan. **Post**.
2. Klik tombol **“Bayar”** di dokumen itu → otomatis buka Jurnal
   Pembayaran dengan nominal full (**edit dulu nominalnya kalau tabel
   bilang “sebagian/partial”** - turunkan ke nominal parsial sesuai
   tabel). Isi Akun Kas/Bank = “1-1100 Bank”. **Post**.
3. **Kalau baru bayar sebagian**: buka lagi dokumen Jurnal
   Pengakuan-nya, cek field “Sisa” sudah berkurang tapi belum 0. Klik
   tombol **“Bayar”** lagi kapan pun mau melunasi sisanya (otomatis
   prefill sisa penuh kali ini) - ulangi sampai “Sisa” = 0.

Penyesuaian Awal Tahun / Penyesuaian Akhir Tahun
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**ERP > Accounting > Tutup Buku > Penyesuaian Awal Tahun** (atau **Akhir
Tahun**), New. Isi baris seperti Jurnal Umum biasa (Akun Debit/Kredit
sesuai tabel). Ketik tanggal berapa saja di tahun yang sesuai —
**setelah Post, tanggal otomatis berubah/terkunci** ke 1 Januari (Awal
Tahun) atau 31 Desember (Akhir Tahun) tahun itu. Ini **disengaja, bukan
bug**.

Proses Tutup Buku
~~~~~~~~~~~~~~~~~

**ERP > Accounting > Tutup Buku > Tutup Buku**, New. Isi “Fiscal Year”
sesuai instruksi (mis. 2024 atau 2025) — field “Closing Date” otomatis
terisi 31 Desember tahun itu. Klik tombol **“Proses Tutup Buku”** (akan
ada popup konfirmasi, klik Ya). Cek status jadi Posted dan ada jurnal
``TUTB-...`` ter-generate.

**Verifikasi tanpa perlu hitung manual**: buka **ERP > Accounting >
Konfigurasi > Chart of Accounts**, cari saldo semua akun tipe
“Pendapatan”/“Beban…” untuk tahun yang baru ditutup — semuanya harus
balik ke pola normal (bukan dicek manual satu-satu, cukup pastikan tidak
ada error saat proses & jurnal ``TUTB`` muncul dengan beberapa baris,
bukan cuma 1).

--------------

Jalankan Skenario
-----------------

Kerjakan
01-transaksi-distributor-ban.md
**bulan per bulan, baris per baris sesuai tanggal**, pakai panduan “Cara
Input” di atas. Beberapa titik penting yang wajib diperhatikan (jangan
dilewat):

1.  **31 Des 2024** — sebelum lanjut ke Januari 2025, cek dulu saldo
    “1-1420 Biaya Dibayar Dimuka” = **Rp 100.000.000** (lihat checkpoint
    di 01).
2.  **Setelah semua transaksi Des 2024 selesai** — proses **Tutup Buku
    Fiscal Year 2024** (lihat instruksi di akhir bagian “2024” pada 01).
    **Jangan tutup buku tahun 2026** (tahun berjalan sekarang) — cuma
    tahun yang sudah lewat penuh (2024, 2025) yang boleh ditutup.
3.  **Setelah PO 5 Feb 2025** — cek produk BAN-A1 sekarang punya 2 harga
    beli berbeda tersimpan di sistem (2 layer). Kalau nanti ada
    transaksi Pengiriman Barang untuk A1 dengan qty yang melewati sisa
    stok dari harga lama, HPP-nya harus otomatis gabungan 2 harga itu —
    ini bukti FIFO jalan benar, **tidak perlu dihitung manual**, cukup
    pastikan tidak error saat posting.
4.  **31 Agustus 2025** — cek saldo “1-1420 Biaya Dibayar Dimuka” = **Rp
    0** (sewa tahun 1 sudah habis diamortisasi).
5.  **18 Agustus 2025** — skenario Retur setelah invoice sudah lunas
    (kasus unik: piutang jadi minus, harus di-refund).
6.  **15 Desember 2025** — skenario Write-off piutang yang sudah 4 bulan
    tidak dibayar.
7.  **Setelah transaksi Des 2025 selesai, JANGAN dulu proses Tutup Buku
    Fiscal Year 2025** — lanjut dulu ke Januari 2026 dengan buku 2025
    masih terbuka (sengaja, lihat catatan “Tutup Buku 2025 SENGAJA
    DITUNDA” di 01). Ini buat mengamati efeknya ke akun “3-1100 Laba
    Ditahan” sebelum vs sesudah ditutup. 7a. **Akhir Januari 2026** —
    sebelum lanjut Februari, cek dulu saldo “3-1100 Laba Ditahan”
    (checkpoint “SEBELUM Tutup Buku 2025” di 01) — harus masih cuma
    refleksi hasil Tutup Buku 2024, belum termasuk 2025. 7b. **Akhir
    Februari 2026** — baru proses **Tutup Buku Fiscal Year 2025** di
    titik ini, lalu cek lagi saldo “3-1100 Laba Ditahan” — sekarang
    harus sudah berubah sebesar hasil bersih 2025.
8.  **Akhir Februari 2026** — cocokkan **Qty On Hand** tiap 9 produk
    dengan tabel “Checkpoint Interim” di 01.
9.  **Maret 2026** — batch khusus penutup gap coverage fitur (Uang Muka,
    Retur Vendor, Write-off Hutang, Pemakaian Sendiri, Stok Opname, 4
    jenis Aktiva Tetap sisanya, Payroll partial). Ikuti sub-bagian
    G.1-G.6 di 01 **berurutan** (G.1 dan G.2 masing-masing punya
    beberapa dokumen berantai yang harus dikerjakan sesuai urutan
    tanggal, jangan diacak). **Perhatikan khusus G.1**: setelah Retur
    Barang Vendor, jangan lupa Pembayaran Vendor #3 (refund, nominal
    negatif) - kalau kelewat, saldo tagihan bakal menggantung negatif.
10. **2 April 2026** — lunasi sisa gaji Maret (payroll partial dari poin
    9).
11. **Setelah semua di atas** — cocokkan **Qty On Hand** tiap 9 produk
    dengan tabel “Checkpoint Akhir” (bukan Interim lagi) di 01. Kalau
    ada yang beda, ada transaksi yang salah/kelewat - telusuri balik
    dari checkpoint terdekat sebelumnya.

--------------

Bagian Tambahan — Edge Case Terpisah (BUKAN bagian cerita PT Roda Sejahtera)
----------------------------------------------------------------------------

⚠️ **Kerjakan di database/instance TERPISAH**, jangan di database yang
sedang menjalankan skenario di atas — karena tes ini mengubah setting
Costing Method secara global, yang akan merusak konsistensi FIFO
skenario utama kalau dilakukan di database yang sama.

[X1] Coba Jual Melebihi Stok (harus DITOLAK)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Buat produk baru “TEST-OVERSELL”, beli stok cuma 5 unit
   (PO→Penerimaan Barang→Post).
2. Coba buat Pengiriman Barang qty **100** (sengaja lebih dari stok),
   klik Post.
3. **Hasil yang Diharapkan**: sistem **menolak** dengan pesan error
   “Stok tidak cukup”. Kalau berhasil ter-posting, ini **BUG SERIUS**,
   laporkan segera.

[X2] Perbandingan FIFO vs Average
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Ubah Settings > Companies > Costing Method jadi **Average**.
2. Buat produk baru “TEST-AVG”. Beli 2x: qty 10 @1.000, lalu qty 10
   @1.500 (2 PO terpisah, masing-masing lewat Penerimaan Barang, Post).
3. Kirim (Pengiriman Barang) qty 15.
4. **Hasil yang Diharapkan**: HPP = 15 × harga rata-rata (1.250) =
   **18.750** — beda dari kalau pakai FIFO (yang akan menghasilkan
   17.500 = 10×1.000 + 5×1.500). Ini membuktikan 2 metode costing
   menghasilkan angka beda seperti seharusnya.
5. **Setelah selesai, kembalikan Costing Method ke FIFO** kalau instance
   ini masih mau dipakai buat testing lain.

[X3] Validasi Penguncian Periode
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Setelah Tutup Buku 2024 diproses (dari skenario utama), coba buat
   Jurnal Umum baru bertanggal di dalam tahun 2024 (mis. 15 Des 2024).
2. **Hasil yang Diharapkan**: sistem **menolak** dengan pesan “periode
   sudah ditutup”. Sebagai pembanding, jurnal bertanggal 2026 (tahun
   belum ditutup) harus tetap **berhasil normal**.

Catatan: Multi-Currency Sengaja TIDAK Dites
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Field kurs/mata uang asing (``currency_id``/``exchange_rate``) ada di
``c18.account.move``, tapi mesin akuntansinya belum melakukan konversi
otomatis ke mata uang company saat agregasi (Trial Balance, Tutup Buku).
Kalau dites, jurnal dalam mata uang asing bakal salah kebaca pas
dihitung saldo. Ini **temuan gap implementasi** (lihat
00-skenario-distributor-ban.md poin
I), bukan sesuatu yang perlu ditest-workaround - laporkan sebagai
catatan, bukan dites langsung.

--------------

Ringkasan Checklist
-------------------

+-----------------+-----------------+-----------------+-----------------+
| No              | Skenario        | Pass/Fail       | Catatan         |
+=================+=================+=================+=================+
| Bagian 0        | Setup data      |                 |                 |
|                 | master          |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
| Nov-Des 2024    | Setup awal +    |                 |                 |
|                 | transaksi       |                 |                 |
|                 | pertama + Tutup |                 |                 |
|                 | Buku 2024       |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
| Jan-Agu 2025    | Transaksi       |                 |                 |
|                 | bulanan + cek   |                 |                 |
|                 | FIFO layering + |                 |                 |
|                 | prepaid rent    |                 |                 |
|                 | habis           |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
| Agu-Des 2025    | Retur,          |                 |                 |
|                 | Write-off, Sewa |                 |                 |
|                 | tahun 2 (Tutup  |                 |                 |
|                 | Buku 2025       |                 |                 |
|                 | DITUNDA)        |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
| Jan 2026        | Transaksi       |                 |                 |
|                 | bulanan +       |                 |                 |
|                 | checkpoint Laba |                 |                 |
|                 | Ditahan SEBELUM |                 |                 |
|                 | Tutup Buku 2025 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
| Feb 2026        | Transaksi       |                 |                 |
|                 | bulanan +       |                 |                 |
|                 | checkpoint      |                 |                 |
|                 | interim stok +  |                 |                 |
|                 | Tutup Buku 2025 |                 |                 |
|                 | + checkpoint    |                 |                 |
|                 | Laba Ditahan    |                 |                 |
|                 | SESUDAH         |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
| Mar-Apr 2026    | Uang Muka,      |                 |                 |
| (G.1-G.6)       | Retur Vendor,   |                 |                 |
|                 | Write-off       |                 |                 |
|                 | Hutang,         |                 |                 |
|                 | Pemakaian       |                 |                 |
|                 | Sendiri, Stok   |                 |                 |
|                 | Opname, Aktiva  |                 |                 |
|                 | Tetap 4 jenis   |                 |                 |
|                 | sisanya,        |                 |                 |
|                 | Payroll partial |                 |                 |
|                 | + checkpoint    |                 |                 |
|                 | akhir           |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
| X1-X3           | Edge case       |                 |                 |
|                 | (database       |                 |                 |
|                 | terpisah)       |                 |                 |
+-----------------+-----------------+-----------------+-----------------+

Kalau semua Pass, modul ``c18_basic_erp`` lolos smoke test manual
skenario realistis. Laporkan yang Fail pakai format bug report di atas.
