Data Transaksi Kronologis - PT Roda Sejahtera (Nov 2024 - Feb 2026)
=====================================================================

Status: draft awal (2026-08-27), belum pernah diinput ke sistem. Lanjutan
dari dokumen "00 - Profile" (baca dulu itu untuk konteks profil
perusahaan/asumsi) - dipakai oleh dokumen "02 - Procedure" sebagai sumber
data yang harus diinput.

Dokumen ini murni **daftar data** (tanggal, dokumen, nominal) - bukan langkah
klik-per-klik. Cara menginput tiap jenis dokumen ada di dokumen "02 -
Procedure".

Master Data Tambahan
-------------------------

**Vendor**: PT Ban Nusantara Distribusi (satu-satunya supplier di skenario
ini).

**Customer (reseller)**, dipakai bergantian:

- Toko Ban Makmur
- UD Roda Mas
- Bengkel Sinar Jaya
- Toko Onderdil Abadi

**Catatan akun**: amortisasi sewa kantor dibebankan ke **6-1600 Beban Sewa**
(akun baru, ditambah 2026-08-28 ke data default CoA - sebelumnya numpang ke
6-1200 Beban Operasional, sudah diganti di seluruh dokumen ini).

Skema Kenaikan Harga Beli (FIFO layering)
-----------------------------------------------

.. list-table::
   :header-rows: 1

   * - SKU
     - Layer 1 (Nov 2024)
     - Layer 2
     - Layer 3
   * - BAN-A1
     - 700.000
     - 730.000 (Feb 2025)
     - 760.000 (Des 2025)
   * - BAN-A2
     - -
     - 750.000 (Jan 2025)
     - 750.000 (Agu 2025, Feb 2026 - harga sama, cuma nambah layer baru)
   * - BAN-A3
     - -
     - 800.000 (Mei 2025)
     - 830.000 (Agu 2025)
   * - BAN-B1
     - 650.000
     - 650.000 (Sep 2025, harga sama)
     - -
   * - BAN-B2
     - -
     - 700.000 (Mar 2025)
     - 725.000 (Apr 2025)
   * - BAN-B3
     - 720.000
     - 720.000 (Nov 2025, harga sama)
     - -
   * - BAN-B4
     - -
     - 780.000 (Jul 2025)
     - 810.000 (Okt 2025)
   * - BAN-C1
     - 900.000
     - 940.000 (Jun 2025)
     - -
   * - BAN-C2
     - 950.000
     - 950.000 (Nov 2025)
     - 990.000 (Jan 2026)

----

2024
--------

November 2024
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 01
     - Modal Saham
     - Setoran modal awal pemilik
     - Rp 1.000.000.000
     - Masuk **Bank**
   * - 05
     - Sewa Kantor Tahun 1
     - Sewa kantor Nov 2024-Okt 2025 (1 tahun, lunas dimuka) -> akun "1-1420
       Biaya Dibayar Dimuka"
     - Rp 120.000.000
     - **Bank**
   * - 05
     - Jurnal Umum
     - Jaminan/deposit sewa kantor (refundable, tidak diamortisasi) - debit
       "1-3100 Jaminan/Deposit", kredit "1-1100 Bank"
     - Rp 20.000.000
     - **Bank**
   * - 06
     - Aktiva Tetap - Pengakuan
     - Perabotan kantor: meja+kursi+lemari+2 laptop+printer -> "1-2300
       Peralatan Kantor"
     - Rp 31.400.000
     - **Bank**
   * - 07
     - Kas Keluar
     - ATK & barang habis pakai (kertas, pulpen, papan tulis) -> "6-1100
       Beban ATK"
     - Rp 2.500.000
     - **Kas**
   * - 20
     - PO -> Penerimaan Barang -> Buat Tagihan -> Pembayaran Vendor (lunas)
     - Stok awal 5 SKU: A1x30@700rb, B1x30@650rb, B3x20@720rb, C1x15@900rb,
       C2x15@950rb
     - Rp 82.650.000
     - **Bank**
   * - 30
     - Jurnal Umum
     - Amortisasi sewa kantor bulan 1 (debit **6-1600 Beban Sewa**, kredit
       1-1420)
     - Rp 10.000.000
     - -
   * - 30
     - Payroll (Pengakuan+Pembayaran)
     - Gaji Nov 2024 (Si A 5.067.381 + Si B 5.574.119)
     - Rp 10.641.500
     - **Bank**
   * - 30
     - Kas Keluar
     - Listrik 1.500.000 + Internet 500.000
     - Rp 2.000.000
     - **Kas**

Desember 2024
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 17
     - SO -> Delivery -> Invoice -> Pembayaran
     - Ke Toko Ban Makmur: A1x10@850rb=8.500.000, B1x10@800rb=8.000.000
     - Rp 16.500.000
     - **Kas**, lunas hari yang sama
   * - 20
     - SO -> Delivery -> Invoice (BELUM dibayar)
     - Ke UD Roda Mas: C1x5@1.080rb=5.400.000, C2x5@1.140rb=5.700.000
     - Rp 11.100.000
     - **Piutang** - dilunasi Jan 2025
   * - 30
     - Jurnal Umum
     - Amortisasi sewa bulan 2
     - Rp 10.000.000
     - -
   * - 30
     - Payroll
     - Gaji Des 2024
     - Rp 10.641.500
     - **Bank**
   * - 30
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

.. note::

   **Checkpoint 31 Des 2024**: Saldo "1-1420 Biaya Dibayar Dimuka" harus =
   **Rp 100.000.000** (120jt - 2x10jt).

.. important::

   **Tutup Buku 2024 (proses sekarang, sebelum lanjut ke Januari 2025)**

   - **Penyesuaian Awal Tahun tidak perlu di sini** (baru dipakai Jan 2025,
     lihat di bawah).
   - **Proses Tutup Buku, Fiscal Year = 2024.** Ini akan menolkan akun
     Pendapatan (dari 2 penjualan Des) dan akun Beban (Sewa, ATK, Gaji,
     Listrik/Internet Nov-Des), selisihnya (rugi, karena baru mulai usaha &
     belum banyak penjualan) pindah ke Laba Ditahan.

----

2025
--------

Januari 2025
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 02
     - Penyesuaian Awal Tahun
     - Koreksi: ada Beban Operasional Des 2024 yang lupa tercatat
     - Rp 300.000
     - -
   * - 05
     - Penerimaan Piutang
     - Pelunasan piutang Des 2024 dari UD Roda Mas (tanpa potongan)
     - Rp 11.100.000
     - **Bank**
   * - 10
     - PO -> ... -> Pembayaran
     - Beli A2x25@750rb (SKU baru pertama kali)
     - Rp 18.750.000
     - **Bank**
   * - 15
     - SO -> ... -> Pembayaran
     - Ke Toko Ban Makmur: A1x8@850rb
     - Rp 6.800.000
     - **Bank**
   * - 22
     - SO -> ... -> Pembayaran
     - Ke UD Roda Mas: B1x6@800rb
     - Rp 4.800.000
     - **Kas**
   * - 31
     - Jurnal Umum
     - Amortisasi sewa bulan 3
     - Rp 10.000.000
     - -
   * - 31
     - Payroll
     - Gaji Jan 2025 (Si A 5.396.791 + Si B 5.936.470)
     - Rp 11.333.261
     - **Bank**
   * - 31
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

Februari 2025
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - PO -> ... -> Pembayaran
     - Beli A1x25@730rb (**harga naik dari 700rb** -> layer FIFO baru)
     - Rp 18.250.000
     - **Bank**
   * - 12
     - SO -> ... -> Pembayaran
     - Ke Bengkel Sinar Jaya: C1x5@1.080rb
     - Rp 5.400.000
     - **Bank**
   * - 20
     - SO -> ... -> Invoice (BELUM dibayar)
     - Ke Toko Onderdil Abadi: A2x10@900rb
     - Rp 9.000.000
     - **Piutang** - dilunasi Mar 2025 dg potongan
   * - 28
     - Jurnal Umum
     - Amortisasi sewa bulan 4
     - Rp 10.000.000
     - -
   * - 28
     - Payroll
     - Gaji Feb 2025
     - Rp 11.333.261
     - **Bank**
   * - 28
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

.. note::

   **Cek FIFO di sini**: setelah PO 05 Feb, produk A1 sekarang punya **2
   layer harga** (700rb sisa dari Nov, 730rb dari Feb). Kalau nanti ada
   penjualan A1 yang qty-nya melewati sisa layer 700rb, HPP-nya harus
   gabungan 2 harga (lihat panduan cek di dokumen "02 - Procedure").

Maret 2025
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - PO -> ... -> Pembayaran
     - Beli B2x25@700rb (SKU baru)
     - Rp 17.500.000
     - **Bank**
   * - 10
     - Penerimaan Piutang (dengan potongan)
     - Pelunasan piutang Feb dari Toko Onderdil Abadi, deduction "Potongan
       tunai" 50.000
     - Nominal bayar 9.000.000, deduction 50.000, net 8.950.000
     - **Bank**
   * - 14
     - SO -> ... -> Pembayaran
     - Ke Toko Ban Makmur: B3x8@870rb
     - Rp 6.960.000
     - **Kas**
   * - 25
     - SO -> ... -> Pembayaran
     - Ke UD Roda Mas: A1x10@850rb
     - Rp 8.500.000
     - **Bank**
   * - 31
     - Jurnal Umum
     - Amortisasi sewa bulan 5
     - Rp 10.000.000
     - -
   * - 31
     - Payroll
     - Gaji Mar 2025
     - Rp 11.333.261
     - **Bank**
   * - 31
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

April 2025
~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - PO -> ... -> Pembayaran
     - Beli B2x20@725rb (**naik dari 700rb**)
     - Rp 14.500.000
     - **Bank**
   * - 12
     - SO -> ... -> Pembayaran
     - Ke Bengkel Sinar Jaya: C2x6@1.140rb
     - Rp 6.840.000
     - **Bank**
   * - 20
     - SO -> ... -> Pembayaran
     - Ke Toko Onderdil Abadi: B2x10@850rb
     - Rp 8.500.000
     - **Kas**
   * - 30
     - Jurnal Umum
     - Amortisasi sewa bulan 6
     - Rp 10.000.000
     - -
   * - 30
     - Payroll
     - Gaji Apr 2025
     - Rp 11.333.261
     - **Bank**
   * - 30
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

Mei 2025
~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - PO -> ... -> Pembayaran
     - Beli A3x20@800rb (SKU baru)
     - Rp 16.000.000
     - **Bank**
   * - 12
     - SO -> ... -> Pembayaran
     - Ke Toko Ban Makmur: A3x8@950rb
     - Rp 7.600.000
     - **Bank**
   * - 20
     - SO -> ... -> Invoice (BELUM dibayar)
     - Ke UD Roda Mas: B1x8@800rb
     - Rp 6.400.000
     - **Piutang** - dilunasi Jun 2025
   * - 31
     - Jurnal Umum
     - Amortisasi sewa bulan 7
     - Rp 10.000.000
     - -
   * - 31
     - Payroll
     - Gaji Mei 2025
     - Rp 11.333.261
     - **Bank**
   * - 31
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

Juni 2025
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - PO -> ... -> Pembayaran
     - Beli C1x15@940rb (**naik dari 900rb**)
     - Rp 14.100.000
     - **Bank**
   * - 08
     - Penerimaan Piutang
     - Pelunasan piutang Mei dari UD Roda Mas (tanpa potongan)
     - Rp 6.400.000
     - **Bank**
   * - 12
     - SO -> ... -> Pembayaran
     - Ke Bengkel Sinar Jaya: C1x6@1.080rb
     - Rp 6.480.000
     - **Bank**
   * - 20
     - SO -> ... -> Pembayaran
     - Ke Toko Onderdil Abadi: A1x10@850rb
     - Rp 8.500.000
     - **Kas**
   * - 30
     - Jurnal Umum
     - Amortisasi sewa bulan 8
     - Rp 10.000.000
     - -
   * - 30
     - Payroll
     - Gaji Jun 2025
     - Rp 11.333.261
     - **Bank**
   * - 30
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

Juli 2025
~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - PO -> ... -> Pembayaran
     - Beli B4x20@780rb (SKU baru)
     - Rp 15.600.000
     - **Bank**
   * - 08
     - Jurnal Umum
     - Terima Pinjaman Bank Jangka Panjang (modal kerja tambahan) - debit
       "1-1100 Bank", kredit "2-2000 Hutang Bank Jangka Panjang"
     - Rp 50.000.000
     - **Bank**
   * - 12
     - SO -> ... -> Pembayaran
     - Ke Toko Ban Makmur: B4x8@930rb
     - Rp 7.440.000
     - **Bank**
   * - 20
     - SO -> ... -> Pembayaran
     - Ke UD Roda Mas: A2x10@900rb
     - Rp 9.000.000
     - **Kas**
   * - 31
     - Jurnal Umum
     - Amortisasi sewa bulan 9
     - Rp 10.000.000
     - -
   * - 31
     - Payroll
     - Gaji Jul 2025
     - Rp 11.333.261
     - **Bank**
   * - 31
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

Agustus 2025
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - PO -> ... -> Pembayaran
     - Beli A3x15@830rb (**naik dari 800rb**)
     - Rp 12.450.000
     - **Bank**
   * - 07
     - PO -> ... -> Pembayaran (tambahan)
     - Beli A2x20@750rb (restock, harga sama)
     - Rp 15.000.000
     - **Bank**
   * - 12
     - SO -> ... -> Pembayaran
     - Ke Bengkel Sinar Jaya: A3x6@950rb
     - Rp 5.700.000
     - **Bank**
   * - 15
     - Jurnal Umum
     - Cicilan Pinjaman Bank #1 - debit "2-2000 Hutang Bank Jangka Panjang"
       2.000.000 (pokok) + debit "9-1000 Beban Bunga" 500.000 (bunga),
       kredit "1-1100 Bank" 2.500.000
     - Rp 2.500.000
     - **Bank**
   * - 18
     - Retur Barang Customer (sudah invoice)
     - Bengkel Sinar Jaya retur A3x2 dari invoice 12 Agu
     - -Rp 1.900.000
     - Refund via Penerimaan Piutang nominal negatif
   * - 20
     - SO -> ... -> Invoice (BELUM dibayar, TIDAK PERNAH LUNAS)
     - Ke Toko Onderdil Abadi: B3x8@870rb
     - Rp 6.960.000
     - **Piutang** - akan di-**write-off** Des 2025
   * - 31
     - Jurnal Umum
     - Amortisasi sewa bulan 10 (**terakhir**, sewa tahun 1 habis)
     - Rp 10.000.000
     - -
   * - 31
     - Payroll
     - Gaji Agu 2025
     - Rp 11.333.261
     - **Bank**
   * - 31
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

.. note::

   **Checkpoint 31 Agu 2025**: Saldo "1-1420 Biaya Dibayar Dimuka" (dari
   sewa tahun 1) harus = **Rp 0** (120jt sudah teramortisasi penuh 10 bulan,
   Nov24-Agu25 = 10 bulan).

September 2025
~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - PO -> ... -> Pembayaran
     - Beli B1x25@650rb (restock, harga sama)
     - Rp 16.250.000
     - **Bank**
   * - 08
     - Jurnal Umum
     - Leasing rak gudang (aset masuk lewat pembiayaan leasing) - debit
       "1-2300 Peralatan Kantor", kredit "2-2100 Hutang Leasing"
     - Rp 15.000.000
     - -
   * - 10
     - Jurnal Umum
     - Cicilan Leasing #1 - debit "2-2100 Hutang Leasing", kredit "1-1100
       Bank"
     - Rp 1.500.000
     - **Bank**
   * - 12
     - SO -> ... -> Pembayaran
     - Ke Toko Ban Makmur: B1x10@800rb
     - Rp 8.000.000
     - **Kas**
   * - 20
     - SO -> ... -> Pembayaran
     - Ke UD Roda Mas: C2x3@1.140rb
     - Rp 3.420.000
     - **Bank**
   * - 30
     - Payroll
     - Gaji Sep 2025
     - Rp 11.333.261
     - **Bank**
   * - 30
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

*(Tidak ada amortisasi sewa bulan ini - sewa tahun 1 sudah habis, sewa tahun
2 belum mulai sampai November.)*

Oktober 2025
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - PO -> ... -> Pembayaran
     - Beli B4x15@810rb (**naik dari 780rb**)
     - Rp 12.150.000
     - **Bank**
   * - 12
     - SO -> ... -> Pembayaran
     - Ke Bengkel Sinar Jaya: B4x8@930rb
     - Rp 7.440.000
     - **Bank**
   * - 15
     - Kas Masuk
     - Terima bunga deposito bank - akun lawan "8-1100 Pendapatan Bunga"
     - Rp 300.000
     - **Bank**
   * - 20
     - SO -> ... -> Pembayaran
     - Ke Toko Ban Makmur: A1x8@850rb
     - Rp 6.800.000
     - **Kas**
   * - 31
     - Payroll
     - Gaji Okt 2025
     - Rp 11.333.261
     - **Bank**
   * - 31
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

November 2025
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 03
     - Sewa Kantor Tahun 2
     - Sewa kantor Nov 2025-Okt 2026 (lunas dimuka lagi)
     - Rp 120.000.000
     - **Bank**
   * - 05
     - PO -> ... -> Pembayaran
     - Beli B3x20@720rb (restock, harga sama)
     - Rp 14.400.000
     - **Bank**
   * - 12
     - SO -> ... -> Pembayaran
     - Ke UD Roda Mas: A2x10@900rb
     - Rp 9.000.000
     - **Bank**
   * - 20
     - SO -> ... -> Pembayaran
     - Ke Toko Onderdil Abadi: C1x5@1.080rb
     - Rp 5.400.000
     - **Kas**
   * - 30
     - Jurnal Umum
     - Amortisasi sewa **tahun 2** bulan 1
     - Rp 10.000.000
     - -
   * - 30
     - Payroll
     - Gaji Nov 2025
     - Rp 11.333.261
     - **Bank**
   * - 30
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

Desember 2025
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - PO -> ... -> Pembayaran
     - Beli A1x20@760rb (**naik dari 730rb**, layer ke-3)
     - Rp 15.200.000
     - **Bank**
   * - 12
     - SO -> ... -> Pembayaran
     - Ke Toko Ban Makmur: B2x10@850rb
     - Rp 8.500.000
     - **Bank**
   * - 15
     - Write-off Piutang
     - Hapuskan piutang Toko Onderdil Abadi dari 20 Agu 2025 (4 bulan tak
       dibayar)
     - Rp 6.960.000
     - -
   * - 20
     - SO -> ... -> Pembayaran
     - Ke Bengkel Sinar Jaya: A1x8@850rb
     - Rp 6.800.000
     - **Kas**
   * - 28
     - Penyesuaian Akhir Tahun
     - Koreksi kecil: tambahan Beban Operasional yang terlewat
     - Rp 500.000
     - -
   * - 31
     - Jurnal Umum
     - Amortisasi sewa tahun 2 bulan 2
     - Rp 10.000.000
     - -
   * - 31
     - Payroll
     - Gaji Des 2025
     - Rp 11.333.261
     - **Bank**
   * - 31
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.000.000
     - **Kas**

.. important::

   **Tutup Buku 2025 (proses sekarang, sebelum lanjut ke Januari 2026)**

   - **Proses Tutup Buku, Fiscal Year = 2025.**

----

2026
--------

Januari 2026
~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - PO -> ... -> Pembayaran
     - Beli C2x15@990rb (**naik dari 950rb**)
     - Rp 14.850.000
     - **Bank**
   * - 12
     - SO -> ... -> Pembayaran
     - Ke UD Roda Mas: A1x8@850rb
     - Rp 6.800.000
     - **Bank**
   * - 20
     - SO -> ... -> Pembayaran
     - Ke Toko Ban Makmur: C2x5@1.140rb
     - Rp 5.700.000
     - **Kas**
   * - 31
     - Jurnal Umum
     - Amortisasi sewa tahun 2 bulan 3
     - Rp 10.000.000
     - -
   * - 31
     - Payroll
     - Gaji Jan 2026 (Si A 5.729.876 + Si B 6.302.864)
     - Rp 12.032.740
     - **Bank**
   * - 31
     - Kas Keluar
     - Listrik (naik dikit) 1.600.000 + Internet 500.000
     - Rp 2.100.000
     - **Kas**

Februari 2026
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - PO -> ... -> Pembayaran
     - Beli A2x20@750rb (restock, harga sama)
     - Rp 15.000.000
     - **Bank**
   * - 12
     - SO -> ... -> Pembayaran
     - Ke Bengkel Sinar Jaya: A2x10@900rb
     - Rp 9.000.000
     - **Bank**
   * - 20
     - SO -> ... -> Pembayaran
     - Ke Toko Onderdil Abadi: B1x6@800rb
     - Rp 4.800.000
     - **Kas**
   * - 28
     - Jurnal Umum
     - Amortisasi sewa tahun 2 bulan 4
     - Rp 10.000.000
     - -
   * - 28
     - Payroll
     - Gaji Feb 2026
     - Rp 12.032.740
     - **Bank**
   * - 28
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.100.000
     - **Kas**

----

Maret 2026 - Batch Penutup Gap Coverage Fitur
--------------------------------------------------

Ditambah 2026-08-28. Bagian normal (1 pembelian + 2 penjualan tiap bulan)
sudah otomatis tercakup oleh transaksi Uang Muka di bawah - tidak ada
tambahan PO/SO polos terpisah bulan ini. 2 Cost Center baru (**Operasional**,
**Gudang**) dipakai nge-tag transaksi di bawah (opsional, boleh kosong juga
kalau tidak sempat).

G.1 Uang Muka Pembelian -> apply DP -> Retur Barang Vendor (setelah invoice, kasus saldo negatif)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 03
     - PO (Confirm saja, belum diterima)
     - Beli B1x20@650rb dari PT Ban Nusantara Distribusi
     - Rp 13.000.000
     - -
   * - 04
     - Uang Muka Pembelian
     - Referensi PO di atas
     - Rp 5.000.000
     - **Bank**
   * - 06
     - Penerimaan Barang -> Buat Tagihan
     - Terima penuh 20 unit B1, jadi Pembelian (Bill)
     - Rp 13.000.000
     - -
   * - 07
     - Pembayaran Vendor #1 (apply DP)
     - Akun Kredit = **"1-1400 Uang Muka Pembelian"** (bukan Kas/Bank) -
       netting DP ke tagihan
     - Rp 5.000.000
     - Akun "1-1400"
   * - 07
     - Pembayaran Vendor #2 (sisa + 2 deduction)
     - Akun Kredit = "1-1100 Bank". Nominal Bayar (baris invoice) =
       8.000.000. Tambah 2 baris Deduction (keduanya **negatif** = penambah):
       (1) "Biaya admin transfer bank" akun "9-1100 Beban Admin Bank"
       -25.000, (2) "Denda keterlambatan bayar" akun "9-1200 Beban Denda"
       -50.000
     - Rp 8.075.000 (net, keluar dari Bank)
     - **Bank**
   * - 10
     - Retur Barang Vendor (sudah invoice, referensi Bill)
     - Retur B1x2 (tagihan sudah lunas penuh -> saldo jadi **negatif**,
       vendor "berhutang balik")
     - -Rp 1.300.000
     - -
   * - 11
     - Pembayaran Vendor #3 (refund, nominal negatif)
     - Baris invoice = Bill yang sama, Nominal Bayar = **-1.300.000**
     - -Rp 1.300.000
     - **Bank** (uang masuk balik)

*(Cara isi Nominal Bayar negatif: sama seperti field biasa, tinggal ketik
tanda minus di depan angkanya.)*

G.2 Uang Muka Penjualan -> apply DP ke invoice akhir
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 05
     - SO (Confirm)
     - Ke Toko Ban Makmur: C1x5@1.080rb
     - Rp 5.400.000
     - -
   * - 06
     - Uang Muka Penjualan
     - Referensi SO di atas
     - Rp 2.000.000
     - **Bank**
   * - 12
     - Delivery -> Invoice
     - Kirim & tagih C1x5 sesuai SO
     - Rp 5.400.000
     - -
   * - 13
     - Penerimaan Piutang #1 (apply DP)
     - Akun Debit = **"2-1200 Uang Muka Penjualan"** - netting DP ke invoice
     - Rp 2.000.000
     - Akun "2-1200"
   * - 13
     - Penerimaan Piutang #2 (sisa)
     - Akun Debit = "1-1100 Bank" - lunasi sisa invoice
     - Rp 3.400.000
     - **Bank**

G.3 Write-off Hutang (sisi Pembelian - belum pernah dites)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 14
     - Pembelian (berdiri sendiri, tanpa PO)
     - Jasa service AC kantor, Akun Debit bebas "6-1200 Beban Operasional"
     - Rp 800.000
     - -
   * - 20
     - Write-off Hutang
     - Vendor tutup, tidak akan menagih - hapuskan penuh
     - Rp 800.000
     - -

G.4 Persediaan - Pemakaian Sendiri & Stok Opname (belum pernah dites)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 15
     - Pemakaian Sendiri
     - A2x1 dipakai buat sample display etalase toko (Cost Center: **Gudang**)
     - -
     - -
   * - 18
     - Stok Opname
     - C1: qty sistem dicek, qty fisik = sistem **-1** (ketemu kurang pas
       hitung fisik, Cost Center: **Gudang**)
     - -
     - -

G.5 Aktiva Tetap - 4 jenis transaksi sisanya (belum pernah dites)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Semua lewat form yang sama (ERP > Accounting > Aktiva Tetap), field "Jenis
Transaksi" beda tiap baris. Simplifikasi: nilai jual/hapus aset diasumsikan
pas sama dengan nilai buku (tidak ada gain/loss) - form Basic cuma 1 pasang
debit/kredit per entry, tidak didesain buat kasus gain/loss multi-akun (itu
baru ada Standard+ dengan register aset).

.. list-table::
   :header-rows: 1

   * - Tgl
     - Jenis Transaksi
     - Akun Debit
     - Akun Kredit
     - Nominal
   * - 21
     - Penyusutan
     - 6-1400 Beban Penyusutan
     - 1-2900 Akumulasi Penyusutan
     - Rp 500.000
   * - 22
     - Penghapusan
     - 1-2900 Akumulasi Penyusutan
     - 1-2300 Peralatan Kantor
     - Rp 3.500.000
   * - 24
     - Penjualan
     - 1-1100 Bank
     - 1-2300 Peralatan Kantor
     - Rp 5.000.000
   * - 26
     - Revaluasi
     - 1-2300 Peralatan Kantor
     - 8-1000 Pendapatan Lain-lain
     - Rp 2.000.000

G.6 Payroll - Pembayaran Sebagian (Partial, belum pernah dites)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 28
     - Jurnal Umum
     - Amortisasi sewa tahun 2 bulan 5 (debit 6-1600, kredit 1-1420)
     - Rp 10.000.000
     - -
   * - 31
     - Payroll - Jurnal Pengakuan
     - Gaji Mar 2026 (Cost Center: **Operasional**)
     - Rp 12.032.740
     - -
   * - 31
     - Payroll - Jurnal Pembayaran #1 (sebagian)
     - Bayar sebagian dulu, sisa Rp 5.032.740 masih hutang
     - Rp 7.000.000
     - **Bank**
   * - 31
     - Kas Keluar
     - Listrik + Internet
     - Rp 2.100.000
     - **Kas**

April 2026 (1 hari) - Lunasi Sisa Gaji Maret
--------------------------------------------------

.. list-table::
   :header-rows: 1

   * - Tgl
     - Dokumen
     - Detail
     - Nominal
     - Bayar
   * - 02
     - Payroll - Jurnal Pembayaran #2 (pelunasan)
     - Lunasi sisa gaji Maret 2026
     - Rp 5.032.740
     - **Bank**

----

Checkpoint Interim - Saldo Stok per SKU (per akhir Februari 2026)
---------------------------------------------------------------------

Ini dihitung murni dari total qty masuk dikurangi qty keluar (tidak butuh
hitung FIFO manual) - cocokkan dengan field **"Qty On Hand"** di form
Product:

.. list-table::
   :header-rows: 1

   * - SKU
     - Total Masuk
     - Total Keluar
     - Saldo Akhir
   * - BAN-A1
     - 30+25+20 = 75
     - 10+8+10+10+10+8+8+8 = 72
     - **13**
   * - BAN-A2
     - 25+20+20 = 65
     - 10+10+10+10 = 40
     - **25**
   * - BAN-A3
     - 20+15 = 35
     - 8+6-2(retur) = 12
     - **23**
   * - BAN-B1
     - 30+25 = 55
     - 10+6+8+10+6 = 40
     - **15**
   * - BAN-B2
     - 25+20 = 45
     - 10+10+10 = 30
     - **25**
   * - BAN-B3
     - 20+20 = 40
     - 8+8 = 16
     - **24**
   * - BAN-B4
     - 20+15 = 35
     - 8+8 = 16
     - **19**
   * - BAN-C1
     - 15+15 = 30
     - 5+5+6+5 = 21
     - **9**
   * - BAN-C2
     - 15+15 = 30
     - 5+6+3+5 = 19
     - **11**

Kalau angka "Qty On Hand" di sistem tidak cocok dengan kolom "Saldo Akhir" di
atas, ada transaksi yang salah input/kelewat - cek ulang dari checkpoint
bulan terdekat sebelumnya.

Checkpoint Akhir - Saldo Stok per SKU (per akhir Maret 2026, setelah batch G)
------------------------------------------------------------------------------------

Perubahan dari checkpoint interim di atas, akibat batch Maret 2026 (G.1
Retur Vendor, G.4 Pemakaian Sendiri + Stok Opname, G.2 Delivery C1):

.. list-table::
   :header-rows: 1

   * - SKU
     - Saldo Interim (Feb 2026)
     - Perubahan Maret
     - Saldo Akhir
   * - BAN-A1
     - 13
     - -
     - **13**
   * - BAN-A2
     - 25
     - -1 (Pemakaian Sendiri)
     - **24**
   * - BAN-A3
     - 23
     - -
     - **23**
   * - BAN-B1
     - 15
     - +20 (PO) -2 (Retur Vendor)
     - **33**
   * - BAN-B2
     - 25
     - -
     - **25**
   * - BAN-B3
     - 24
     - -
     - **24**
   * - BAN-B4
     - 19
     - -
     - **19**
   * - BAN-C1
     - 9
     - -1 (Stok Opname) -5 (Delivery G.2)
     - **3**
   * - BAN-C2
     - 11
     - -
     - **11**

Checkpoint Piutang/Hutang Outstanding (per akhir Maret/April 2026)
-----------------------------------------------------------------------

Semua piutang/hutang/uang muka yang dibuat di skenario ini (termasuk batch
Maret) sudah **lunas, di-write-off, atau di-apply penuh** - tidak ada Sisa
Piutang/Sisa Tagihan yang menggantung, kecuali kalau ada kesalahan input.
Perhatikan khusus G.1: setelah Retur Barang Vendor menyebabkan saldo tagihan
B1 jadi negatif, **wajib** ada Pembayaran Vendor #3 (refund, nominal
negatif) supaya kembali ke 0 - kalau langkah ini kelewat, akan ada Sisa
Tagihan minus yang menggantung.

**Catatan**: "2-2000 Hutang Bank Jangka Panjang" dan "2-2100 Hutang Leasing"
sengaja **dibiarkan bersaldo** (belum lunas penuh) per akhir skenario -
realistis untuk pinjaman jangka panjang, bukan kesalahan input.

Cakupan Akun (ditambah 2026-08-28)
---------------------------------------

7 akun CoA yang sebelumnya tidak tersentuh sama sekali kini ikut dilewati
transaksi (tidak mempengaruhi checkpoint stok, semua transaksi ini murni
Kas/Bank/GL):

.. list-table::
   :header-rows: 1

   * - Akun
     - Transaksi
     - Tanggal
   * - 1-3100 Jaminan/Deposit
     - Jaminan sewa kantor
     - 05 Nov 2024
   * - 2-2000 Hutang Bank Jangka Panjang
     - Terima pinjaman + cicilan #1
     - 08 Jul 2025, 15 Agu 2025
   * - 9-1000 Beban Bunga
     - Bunga cicilan pinjaman bank
     - 15 Agu 2025
   * - 2-2100 Hutang Leasing
     - Leasing rak gudang + cicilan #1
     - 08 & 10 Sep 2025
   * - 8-1100 Pendapatan Bunga
     - Bunga deposito bank
     - 15 Okt 2025
   * - 9-1100 Beban Admin Bank
     - Deduction Pembayaran Vendor #2
     - 07 Mar 2026 (G.1)
   * - 9-1200 Beban Denda
     - Deduction Pembayaran Vendor #2
     - 07 Mar 2026 (G.1)

Akun yang **masih** tidak tersentuh (dianggap wajar, di luar scope skenario
ini): PPN Masukan/Keluaran & Hutang Pajak (fitur PPN belum dirancang),
Tanah/Bangunan/Kendaraan/Aktiva Lain-lain (tidak ada pembelian
properti/kendaraan), Laba Tahun Berjalan (by design tidak di-post manual),
Dividen, Balancing Account.
