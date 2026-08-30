# Data Transaksi Kronologis - PT Roda Sejahtera (Nov 2024 - Apr 2026)

Status: **dieksekusi penuh & terverifikasi (2026-08-30)** — lihat [`notes/claude-notes/last-session.md`](../../notes/claude-notes/last-session.md) poin 13-15 untuk jejak keputusan lengkap. Lanjutan dari [00-skenario-distributor-ban.md](00-skenario-distributor-ban.md) (baca dulu itu untuk konteks profil perusahaan/asumsi) — dipakai oleh [02-prosedur-testing.md](02-prosedur-testing.md) sebagai sumber data yang harus diinput.

Dokumen ini murni **daftar data** (tanggal, dokumen, nominal) — bukan langkah klik-per-klik. Cara menginput tiap jenis dokumen ada di 02.

## Master Data Tambahan

**Vendor**: PT Ban Nusantara Distribusi (satu-satunya supplier di skenario ini).

**Customer (reseller)**, dipakai bergantian:
- Toko Ban Makmur
- UD Roda Mas
- Bengkel Sinar Jaya
- Toko Onderdil Abadi

**Catatan akun**: amortisasi sewa kantor dibebankan ke **6-1600 Beban Sewa** (akun baru, ditambah 2026-08-28 ke data default CoA).

## Skema Harga

**Kenaikan harga beli** (FIFO layering) — landai, ~1-2% per ~3 bulan, cuma SKU yang memang naik (restock-harga-sama tetap sama):

| SKU | Layer 1 (Nov 2024) | Layer 2 | Layer 3 |
|---|---|---|---|
| BAN-A1 | 700.000 | **710.000** (Feb 2025, +1,43%) | **720.000** (Des 2025, +1,41%) |
| BAN-A2 | - | 750.000 (Jan 2025) | 750.000 (sama, Agu 2025 & Feb 2026) |
| BAN-A3 | - | 800.000 (Mei 2025) | **810.000** (Agu 2025, +1,25%) |
| BAN-B1 | 650.000 | 650.000 (sama, Sep 2025) | - |
| BAN-B2 | - | 700.000 (Mar 2025) | **710.000** (Apr 2025, +1,43%) |
| BAN-B3 | 720.000 | 720.000 (sama, Nov 2025) | - |
| BAN-B4 | - | 780.000 (Jul 2025) | **790.000** (Okt 2025, +1,28%) |
| BAN-C1 | 900.000 | **915.000** (Jun 2025, +1,67%) | - |
| BAN-C2 | 950.000 | 950.000 (sama, Nov 2025) | **965.000** (Jan 2026, +1,58%) |

**Harga jual** — markup 40% dari harga beli dasar (Layer 1) tiap SKU, **FIXED** sepanjang skenario (tidak ikut naik walau harga beli naik di atas):

| SKU | Harga Beli Dasar | Harga Jual |
|---|---|---|
| BAN-A1 | 700.000 | 980.000 |
| BAN-A2 | 750.000 | 1.050.000 |
| BAN-A3 | 800.000 | 1.120.000 |
| BAN-B1 | 650.000 | 910.000 |
| BAN-B2 | 700.000 | 980.000 |
| BAN-B3 | 720.000 | 1.008.000 |
| BAN-B4 | 780.000 | 1.092.000 |
| BAN-C1 | 900.000 | 1.260.000 |
| BAN-C2 | 950.000 | 1.330.000 |

Qty tiap baris PO/SO di seluruh skenario relatif besar (puluhan-ratusan unit per transaksi) — dipilih supaya laba kotor bulanan cukup menutup beban tetap (gaji 2 karyawan + sewa + listrik/internet ≈ Rp 23-24 juta/bulan), bukan angka sembarang. Hasil akhir: **kedua tahun (2024 & 2025) laba** — lihat bagian "4 Tema" di bawah.

## 4 Tema Perpetual/Periodik × FIFO/Average (2026-08-30)

Skenario ini dijalankan di **4 kombinasi** setting `inventory_system` (Perpetual/Periodik) × `costing_method` (FIFO/Average). Semua transaksi non-produk (Kas Bank, Jurnal Umum, Payroll, Aktiva Tetap, Uang Muka, Pembayaran/Penerimaan, Write-off, Tutup Buku, konfirmasi PO/SO) **tidak terpengaruh sama sekali** oleh axis ini — cuma 7 jenis dokumen yang menggerakkan stok fisik (Penerimaan Barang, Pengiriman Barang, Pemakaian Sendiri, Stok Opname, Retur Vendor, Retur Customer, Penjualan langsung) yang kena efek.

**Fakta teknis penting**: begitu `inventory_system=periodic` aktif, setting `costing_method` (FIFO/Average) **sama sekali tidak dibaca** oleh mesin costing (`product.py` cek `inventory_system` duluan, langsung branch ke jalur periodik tanpa pernah menengok `costing_method`). Jadi dari 4 kombinasi yang kelihatannya mungkin, cuma **3 yang benar-benar beda perilaku**:

| Tema | Database | Hasil 2024 | Hasil 2025 |
|---|---|---|---|
| 1. Perpetual-FIFO | `test-roda-perpetual-fifo` | Laba 6.817.000 | Laba 3.386.868 |
| 2. Perpetual-Average | `test-roda-perpetual-avg` | Laba 6.817.000 | Laba 1.673.178 |
| 3. Periodik-FIFO | `test-roda-periodik-fifo` | Laba 6.817.000 | Laba 4.346.868 |
| 4. Periodik-Average | `test-roda-periodik-avg` | Laba 6.817.000 | Laba 4.346.868 (**identik Tema 3**, dibuktikan empiris - script sama persis, cuma ganti `costing_method`) |

Tema 1 & 2 pakai script identik, cuma beda 1 setting company saat setup, tidak ada perubahan skenario. Tema 3 & 4 butuh 1 tambahan: **jadwal closing Stok Opname periodik** (lihat di bawah), krn HPP di mode Periodik cuma diakui saat Opname, bukan per-transaksi seperti Perpetual.

### Jadwal Closing Periodik (Tema 3 & 4 saja)

Cadence **tahunan** (selaras Tutup Buku), qty fisik = qty sistem (tanpa selisih - murni titik pengakuan nilai, bukan uji selisih fisik):

- **31 Des 2024** — opname 5 SKU yang sudah pernah dibeli sejak PO 20 Nov 2024 (A1@700rb, B1@650rb, B3@720rb, C1@900rb, C2@950rb harga Layer 1 dasar, blm ada kenaikan). 4 SKU lain (A2/A3/B2/B4) belum pernah dibeli di 2024, dilewati.
- **31 Des 2025** — opname semua 9 SKU, harga = harga beli terakhir yang diketahui per SKU per tanggal ini: A1@720rb, A2@750rb, A3@810rb, B1@650rb, B2@710rb, B3@720rb, B4@790rb, C1@915rb, C2@950rb.
- **Maret 2026 (G.4)** — opname C1 yang sudah ada di skenario (selisih -1, TETAP dipakai apa adanya termasuk di Tema 1/2) ditambah `unit_cost=915rb` (wajib diisi manual di mode Periodik, beda dari Perpetual yang otomatis baca `_last_cost()` dari layer FIFO). 8 SKU lain di 2026 sengaja dibiarkan belum ditutup (selaras 2026 yang juga belum di-Tutup-Buku).

**Verifikasi tambahan khusus Periodik**: dicek `c18.stock.layer` (tabel FIFO) benar-benar **0 baris** sepanjang skenario — konfirmasi mesin FIFO per-layer memang nonaktif total di mode ini, bukan cuma tidak dipakai kebetulan.

---

## 2024

### November 2024

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 01 | Modal Saham | Setoran modal awal pemilik | Rp 1.000.000.000 | **Bank** |
| 05 | Sewa Kantor Tahun 1 | Sewa kantor Nov 2024-Okt 2025 (1 tahun, lunas dimuka) → akun "1-1420 Biaya Dibayar Dimuka" | Rp 120.000.000 | **Bank** |
| 05 | Jurnal Umum | Jaminan/deposit sewa kantor (refundable, tidak diamortisasi) — debit "1-3100 Jaminan/Deposit", kredit "1-1100 Bank" | Rp 20.000.000 | **Bank** |
| 06 | Aktiva Tetap - Pengakuan | Perabotan kantor: meja+kursi+lemari+2 laptop+printer → "1-2300 Peralatan Kantor" | Rp 31.400.000 | **Bank** |
| 07 | Kas Keluar | ATK & barang habis pakai (kertas, pulpen, papan tulis) → "6-1100 Beban ATK" | Rp 2.500.000 | **Kas** |
| 20 | PO → Penerimaan Barang → Buat Tagihan → Pembayaran Vendor (lunas) | Stok awal 5 SKU: A1×180@700rb, B1×180@650rb, B3×120@720rb, C1×90@900rb, C2×90@950rb | Rp 495.900.000 | **Bank** |
| 30 | Jurnal Umum | Amortisasi sewa kantor bulan 1 (debit **6-1600 Beban Sewa**, kredit 1-1420) | Rp 10.000.000 | - |
| 30 | Payroll (Pengakuan+Pembayaran) | Gaji Nov 2024 (Si A 5.067.381 + Si B 5.574.119) | Rp 10.641.500 | **Bank** |
| 30 | Kas Keluar | Listrik 1.500.000 + Internet 500.000 | Rp 2.000.000 | **Kas** |

### Desember 2024

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 17 | SO → Delivery → Invoice → Pembayaran | Ke Toko Ban Makmur: A1×60@980rb=58.800.000, B1×60@910rb=54.600.000 | Rp 113.400.000 | **Kas**, lunas hari yang sama |
| 20 | SO → Delivery → Invoice (BELUM dibayar) | Ke UD Roda Mas: C1×30@1.260rb=37.800.000, C2×30@1.330rb=39.900.000 | Rp 77.700.000 | **Piutang** — dilunasi Jan 2025 |
| 30 | Jurnal Umum | Amortisasi sewa bulan 2 | Rp 10.000.000 | - |
| 30 | Payroll | Gaji Des 2024 | Rp 10.641.500 | **Bank** |
| 30 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

**Checkpoint 31 Des 2024**: Saldo "1-1420 Biaya Dibayar Dimuka" harus = **Rp 100.000.000** (120jt − 2×10jt).

### ⭐ Tutup Buku 2024 (proses sekarang, sebelum lanjut ke Januari 2025)
- **Penyesuaian Awal Tahun tidak perlu di sini** (baru dipakai Jan 2025, lihat di bawah).
- **Proses Tutup Buku, Fiscal Year = 2024.** Menolkan akun Pendapatan & Beban tahun 2024, hasil bersih pindah ke Laba Ditahan.

---

## 2025

### Januari 2025

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 02 | Penyesuaian Awal Tahun | Koreksi: ada Beban Operasional Des 2024 yang lupa tercatat | Rp 300.000 | - |
| 05 | Penerimaan Piutang | Pelunasan piutang Des 2024 dari UD Roda Mas (tanpa potongan) | Rp 77.700.000 | **Bank** |
| 10 | PO → ... → Pembayaran | Beli A2×150@750rb (SKU baru pertama kali) | Rp 112.500.000 | **Bank** |
| 15 | SO → ... → Pembayaran | Ke Toko Ban Makmur: A1×48@980rb | Rp 47.040.000 | **Bank** |
| 22 | SO → ... → Pembayaran | Ke UD Roda Mas: B1×36@910rb | Rp 32.760.000 | **Kas** |
| 31 | Jurnal Umum | Amortisasi sewa bulan 3 | Rp 10.000.000 | - |
| 31 | Payroll | Gaji Jan 2025 (Si A 5.396.791 + Si B 5.936.470) | Rp 11.333.261 | **Bank** |
| 31 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

### Februari 2025

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | PO → ... → Pembayaran | Beli A1×150@710rb (**harga naik dari 700rb** → layer FIFO baru) | Rp 106.500.000 | **Bank** |
| 12 | SO → ... → Pembayaran | Ke Bengkel Sinar Jaya: C1×30@1.260rb | Rp 37.800.000 | **Bank** |
| 20 | SO → ... → Invoice (BELUM dibayar) | Ke Toko Onderdil Abadi: A2×60@1.050rb | Rp 63.000.000 | **Piutang** — dilunasi Mar 2025 dg potongan |
| 28 | Jurnal Umum | Amortisasi sewa bulan 4 | Rp 10.000.000 | - |
| 28 | Payroll | Gaji Feb 2025 | Rp 11.333.261 | **Bank** |
| 28 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

> ⭐ **Cek FIFO di sini**: setelah PO 05 Feb, produk A1 sekarang punya **2 layer harga** (700rb sisa dari Nov, 710rb dari Feb). Kalau nanti ada penjualan A1 yang qty-nya melewati sisa layer 700rb, HPP-nya harus gabungan 2 harga (lihat panduan cek di 02).

### Maret 2025

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | PO → ... → Pembayaran | Beli B2×150@700rb (SKU baru) | Rp 105.000.000 | **Bank** |
| 10 | Penerimaan Piutang (dengan potongan) | Pelunasan piutang Feb dari Toko Onderdil Abadi, deduction "Potongan tunai" 50.000 | Nominal bayar Rp 63.000.000, deduction Rp 50.000, net Rp 62.950.000 | **Bank** |
| 14 | SO → ... → Pembayaran | Ke Toko Ban Makmur: B3×48@1.008rb | Rp 48.384.000 | **Kas** |
| 25 | SO → ... → Pembayaran | Ke UD Roda Mas: A1×60@980rb | Rp 58.800.000 | **Bank** |
| 31 | Jurnal Umum | Amortisasi sewa bulan 5 | Rp 10.000.000 | - |
| 31 | Payroll | Gaji Mar 2025 | Rp 11.333.261 | **Bank** |
| 31 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

### April 2025

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | PO → ... → Pembayaran | Beli B2×120@710rb (**naik dari 700rb**) | Rp 85.200.000 | **Bank** |
| 12 | SO → ... → Pembayaran | Ke Bengkel Sinar Jaya: C2×36@1.330rb | Rp 47.880.000 | **Bank** |
| 20 | SO → ... → Pembayaran | Ke Toko Onderdil Abadi: B2×60@980rb | Rp 58.800.000 | **Kas** |
| 30 | Jurnal Umum | Amortisasi sewa bulan 6 | Rp 10.000.000 | - |
| 30 | Payroll | Gaji Apr 2025 | Rp 11.333.261 | **Bank** |
| 30 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

### Mei 2025

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | PO → ... → Pembayaran | Beli A3×120@800rb (SKU baru) | Rp 96.000.000 | **Bank** |
| 12 | SO → ... → Pembayaran | Ke Toko Ban Makmur: A3×48@1.120rb | Rp 53.760.000 | **Bank** |
| 20 | SO → ... → Invoice (BELUM dibayar) | Ke UD Roda Mas: B1×48@910rb | Rp 43.680.000 | **Piutang** — dilunasi Jun 2025 |
| 31 | Jurnal Umum | Amortisasi sewa bulan 7 | Rp 10.000.000 | - |
| 31 | Payroll | Gaji Mei 2025 | Rp 11.333.261 | **Bank** |
| 31 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

### Juni 2025

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | PO → ... → Pembayaran | Beli C1×90@915rb (**naik dari 900rb**) | Rp 82.350.000 | **Bank** |
| 08 | Penerimaan Piutang | Pelunasan piutang Mei dari UD Roda Mas (tanpa potongan) | Rp 43.680.000 | **Bank** |
| 12 | SO → ... → Pembayaran | Ke Bengkel Sinar Jaya: C1×36@1.260rb | Rp 45.360.000 | **Bank** |
| 20 | SO → ... → Pembayaran | Ke Toko Onderdil Abadi: A1×60@980rb | Rp 58.800.000 | **Kas** |
| 30 | Jurnal Umum | Amortisasi sewa bulan 8 | Rp 10.000.000 | - |
| 30 | Payroll | Gaji Jun 2025 | Rp 11.333.261 | **Bank** |
| 30 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

### Juli 2025

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | PO → ... → Pembayaran | Beli B4×120@780rb (SKU baru) | Rp 93.600.000 | **Bank** |
| 08 | Jurnal Umum | Terima Pinjaman Bank Jangka Panjang (modal kerja tambahan) — debit "1-1100 Bank", kredit "2-2000 Hutang Bank Jangka Panjang" | Rp 50.000.000 | **Bank** |
| 12 | SO → ... → Pembayaran | Ke Toko Ban Makmur: B4×48@1.092rb | Rp 52.416.000 | **Bank** |
| 20 | SO → ... → Pembayaran | Ke UD Roda Mas: A2×60@1.050rb | Rp 63.000.000 | **Kas** |
| 31 | Jurnal Umum | Amortisasi sewa bulan 9 | Rp 10.000.000 | - |
| 31 | Payroll | Gaji Jul 2025 | Rp 11.333.261 | **Bank** |
| 31 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

### Agustus 2025

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | PO → ... → Pembayaran | Beli A3×90@810rb (**naik dari 800rb**) | Rp 72.900.000 | **Bank** |
| 07 | PO → ... → Pembayaran (tambahan) | Beli A2×120@750rb (restock, harga sama) | Rp 90.000.000 | **Bank** |
| 12 | SO → ... → Pembayaran | Ke Bengkel Sinar Jaya: A3×36@1.120rb | Rp 40.320.000 | **Bank** |
| 15 | Jurnal Umum | Cicilan Pinjaman Bank #1 — debit "2-2000 Hutang Bank Jangka Panjang" 2.000.000 (pokok) + debit "9-1000 Beban Bunga" 500.000 (bunga), kredit "1-1100 Bank" 2.500.000 | Rp 2.500.000 | **Bank** |
| 18 | Retur Barang Customer (sudah invoice) | Bengkel Sinar Jaya retur A3×12 dari invoice 12 Agu | −Rp 13.440.000 | Refund via Penerimaan Piutang nominal negatif |
| 20 | SO → ... → Invoice (BELUM dibayar, TIDAK PERNAH LUNAS) | Ke Toko Onderdil Abadi: B3×48@1.008rb | Rp 48.384.000 | **Piutang** — akan di-**write-off** Des 2025 |
| 31 | Jurnal Umum | Amortisasi sewa bulan 10 | Rp 10.000.000 | - |
| 31 | Payroll | Gaji Agu 2025 | Rp 11.333.261 | **Bank** |
| 31 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

### September 2025

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | PO → ... → Pembayaran | Beli B1×150@650rb (restock, harga sama) | Rp 97.500.000 | **Bank** |
| 08 | Jurnal Umum | Leasing rak gudang (aset masuk lewat pembiayaan leasing) — debit "1-2300 Peralatan Kantor", kredit "2-2100 Hutang Leasing" | Rp 15.000.000 | - |
| 10 | Jurnal Umum | Cicilan Leasing #1 — debit "2-2100 Hutang Leasing", kredit "1-1100 Bank" | Rp 1.500.000 | **Bank** |
| 12 | SO → ... → Pembayaran | Ke Toko Ban Makmur: B1×60@910rb | Rp 54.600.000 | **Kas** |
| 20 | SO → ... → Pembayaran | Ke UD Roda Mas: C2×18@1.330rb | Rp 23.940.000 | **Bank** |
| 30 | Jurnal Umum | Amortisasi sewa bulan 11 | Rp 10.000.000 | - |
| 30 | Payroll | Gaji Sep 2025 | Rp 11.333.261 | **Bank** |
| 30 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

### Oktober 2025

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | PO → ... → Pembayaran | Beli B4×90@790rb (**naik dari 780rb**) | Rp 71.100.000 | **Bank** |
| 12 | SO → ... → Pembayaran | Ke Bengkel Sinar Jaya: B4×48@1.092rb | Rp 52.416.000 | **Bank** |
| 15 | Kas Masuk | Terima bunga deposito bank — akun lawan "8-1100 Pendapatan Bunga" | Rp 300.000 | **Bank** |
| 20 | SO → ... → Pembayaran | Ke Toko Ban Makmur: A1×48@980rb | Rp 47.040.000 | **Kas** |
| 31 | Jurnal Umum | Amortisasi sewa bulan 12 (**terakhir**, sewa tahun 1 habis) | Rp 10.000.000 | - |
| 31 | Payroll | Gaji Okt 2025 | Rp 11.333.261 | **Bank** |
| 31 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

**Checkpoint 31 Okt 2025**: Saldo "1-1420 Biaya Dibayar Dimuka" (dari sewa tahun 1) harus = **Rp 0** (120jt teramortisasi penuh 12 bulan, Nov24-Okt25).

### November 2025

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 03 | Sewa Kantor Tahun 2 | Sewa kantor Nov 2025-Okt 2026 (lunas dimuka lagi) | Rp 120.000.000 | **Bank** |
| 05 | PO → ... → Pembayaran | Beli B3×120@720rb (restock, harga sama) | Rp 86.400.000 | **Bank** |
| 12 | SO → ... → Pembayaran | Ke UD Roda Mas: A2×60@1.050rb | Rp 63.000.000 | **Bank** |
| 20 | SO → ... → Pembayaran | Ke Toko Onderdil Abadi: C1×30@1.260rb | Rp 37.800.000 | **Kas** |
| 30 | Jurnal Umum | Amortisasi sewa **tahun 2** bulan 1 | Rp 10.000.000 | - |
| 30 | Payroll | Gaji Nov 2025 | Rp 11.333.261 | **Bank** |
| 30 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

### Desember 2025

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | PO → ... → Pembayaran | Beli A1×120@720rb (**naik dari 710rb**, layer ke-3) | Rp 86.400.000 | **Bank** |
| 12 | SO → ... → Pembayaran | Ke Toko Ban Makmur: B2×60@980rb | Rp 58.800.000 | **Bank** |
| 15 | Write-off Piutang | Hapuskan piutang Toko Onderdil Abadi dari 20 Agu 2025 (4 bulan tak dibayar) | Rp 48.384.000 | - |
| 20 | SO → ... → Pembayaran | Ke Bengkel Sinar Jaya: A1×48@980rb | Rp 47.040.000 | **Kas** |
| 28 | Penyesuaian Akhir Tahun | Koreksi kecil: tambahan Beban Operasional yang terlewat | Rp 500.000 | - |
| 31 | Jurnal Umum | Amortisasi sewa tahun 2 bulan 2 | Rp 10.000.000 | - |
| 31 | Payroll | Gaji Des 2025 | Rp 11.333.261 | **Bank** |
| 31 | Kas Keluar | Listrik + Internet | Rp 2.000.000 | **Kas** |

### ⭐ Tutup Buku 2025 SENGAJA DITUNDA
**Jangan proses Tutup Buku Fiscal Year 2025 di titik ini** — lanjut dulu ke transaksi Januari-Februari 2026 dengan buku 2025 masih terbuka (belum ditutup). Tujuannya: mengamati bagaimana saldo akun **"3-1100 Laba Ditahan"** terlihat di laporan/Chart of Accounts kalau dibuka di Januari 2026 **sebelum** Tutup Buku 2025 diproses, dibandingkan **sesudahnya** — lihat checkpoint di akhir bagian Februari 2026 di bawah untuk instruksi proses Tutup Buku 2025 yang sebenarnya (ditunda sampai situ, bukan dihapus).

Ini aman secara sistem — penguncian periode cuma memblokir tanggal ≤ tanggal Tutup Buku terakhir yang sudah posted (saat ini masih 31 Des 2024 dari Tutup Buku 2024), jadi transaksi 2026 tetap bisa diinput normal walau 2025 belum ditutup.

---

## 2026

### Januari 2026

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | PO → ... → Pembayaran | Beli C2×90@965rb (**naik dari 950rb**) | Rp 86.850.000 | **Bank** |
| 12 | SO → ... → Pembayaran | Ke UD Roda Mas: A1×48@980rb | Rp 47.040.000 | **Bank** |
| 20 | SO → ... → Pembayaran | Ke Toko Ban Makmur: C2×30@1.330rb | Rp 39.900.000 | **Kas** |
| 31 | Jurnal Umum | Amortisasi sewa tahun 2 bulan 3 | Rp 10.000.000 | - |
| 31 | Payroll | Gaji Jan 2026 (Si A 5.729.876 + Si B 6.302.864) | Rp 12.032.740 | **Bank** |
| 31 | Kas Keluar | Listrik (naik dikit) 1.600.000 + Internet 500.000 | Rp 2.100.000 | **Kas** |

### ⭐ Checkpoint: Cek Laba Ditahan SEBELUM Tutup Buku 2025
- Buka **ERP > Accounting > Konfigurasi > Chart of Accounts**, cari akun **"3-1100 Laba Ditahan"**, catat saldonya.
- **Yang diharapkan** (Tema 1, Perpetual-FIFO): saldo mencerminkan hasil Tutup Buku 2024 (laba 6.817.000) — **BELUM** termasuk hasil operasional 2025, karena akun Pendapatan/Beban 2025 belum di-nolkan (Tutup Buku 2025 sengaja ditunda).
- Catat angka ini — nanti dibandingkan lagi setelah Tutup Buku 2025 diproses (checkpoint di akhir Februari 2026).

### Februari 2026

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | PO → ... → Pembayaran | Beli A2×120@750rb (restock, harga sama) | Rp 90.000.000 | **Bank** |
| 12 | SO → ... → Pembayaran | Ke Bengkel Sinar Jaya: A2×60@1.050rb | Rp 63.000.000 | **Bank** |
| 20 | SO → ... → Pembayaran | Ke Toko Onderdil Abadi: B1×36@910rb | Rp 32.760.000 | **Kas** |
| 28 | Jurnal Umum | Amortisasi sewa tahun 2 bulan 4 | Rp 10.000.000 | - |
| 28 | Payroll | Gaji Feb 2026 | Rp 12.032.740 | **Bank** |
| 28 | Kas Keluar | Listrik + Internet | Rp 2.100.000 | **Kas** |

### ⭐ Tutup Buku 2025 (baru diproses di sini, ditunda dari akhir 2025)
- **Proses Tutup Buku, Fiscal Year = 2025.**
- Setelah posted, buka lagi **"3-1100 Laba Ditahan"** di Chart of Accounts — bandingkan dengan angka yang dicatat di checkpoint akhir Januari 2026. Saldonya sekarang harus **berubah** sebesar hasil bersih (Pendapatan − Beban) tahun 2025 — kalau angkanya sama persis dengan sebelum ditutup, berarti proses Tutup Buku 2025 tidak jalan/gagal diam-diam. (Tema 1: berubah dari refleksi 6.817.000 jadi refleksi 6.817.000+3.386.868=10.203.868 kumulatif.)

---

## Maret 2026 — Batch Penutup Gap Coverage Fitur

Bagian normal (1 pembelian + 2 penjualan tiap bulan) sudah otomatis tercakup oleh transaksi Uang Muka di bawah — tidak ada tambahan PO/SO polos terpisah bulan ini. 2 Cost Center baru (**Operasional**, **Gudang**) dipakai nge-tag transaksi di bawah (opsional, boleh kosong juga kalau tidak sempat).

### G.1 Uang Muka Pembelian → apply DP → Retur Barang Vendor (setelah invoice, kasus saldo negatif)

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 03 | PO (Confirm saja, belum diterima) | Beli B1×120@650rb dari PT Ban Nusantara Distribusi | Rp 78.000.000 | - |
| 04 | Uang Muka Pembelian | Referensi PO di atas | Rp 5.000.000 | **Bank** |
| 06 | Penerimaan Barang → Buat Tagihan | Terima penuh 120 unit B1, jadi Pembelian (Bill) | Rp 78.000.000 | - |
| 07 | Pembayaran Vendor #1 (apply DP) | Akun Kredit = **"1-1400 Uang Muka Pembelian"** (bukan Kas/Bank) — netting DP ke tagihan | Rp 5.000.000 | Akun "1-1400" |
| 07 | Pembayaran Vendor #2 (sisa + 2 deduction) | Akun Kredit = "1-1100 Bank". Nominal Bayar (baris invoice) = 73.000.000. Tambah 2 baris Deduction (keduanya **negatif** = penambah): (1) "Biaya admin transfer bank" akun "9-1100 Beban Admin Bank" −25.000, (2) "Denda keterlambatan bayar" akun "9-1200 Beban Denda" −50.000 | Rp 73.075.000 (net, keluar dari Bank) | **Bank** |
| 10 | Retur Barang Vendor (sudah invoice, referensi Bill) | Retur B1×12 (tagihan sudah lunas penuh → saldo jadi **negatif**, vendor "berhutang balik") | −Rp 7.800.000 | - |
| 11 | Pembayaran Vendor #3 (refund, nominal negatif) | Baris invoice = Bill yang sama, Nominal Bayar = **−7.800.000** | −Rp 7.800.000 | **Bank** (uang masuk balik) |

*(Cara isi Nominal Bayar negatif: sama seperti field biasa, tinggal ketik tanda minus di depan angkanya.)*

### G.2 Uang Muka Penjualan → apply DP ke invoice akhir

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 05 | SO (Confirm) | Ke Toko Ban Makmur: C1×30@1.260rb | Rp 37.800.000 | - |
| 06 | Uang Muka Penjualan | Referensi SO di atas | Rp 2.000.000 | **Bank** |
| 12 | Delivery → Invoice | Kirim & tagih C1×30 sesuai SO | Rp 37.800.000 | - |
| 13 | Penerimaan Piutang #1 (apply DP) | Akun Debit = **"2-1200 Uang Muka Penjualan"** — netting DP ke invoice | Rp 2.000.000 | Akun "2-1200" |
| 13 | Penerimaan Piutang #2 (sisa) | Akun Debit = "1-1100 Bank" — lunasi sisa invoice | Rp 35.800.000 | **Bank** |

### G.3 Write-off Hutang (sisi Pembelian)

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 14 | Pembelian (berdiri sendiri, tanpa PO) | Jasa service AC kantor, Akun Debit bebas "6-1200 Beban Operasional" | Rp 800.000 | - |
| 20 | Write-off Hutang | Vendor tutup, tidak akan menagih — hapuskan penuh | Rp 800.000 | - |

### G.4 Persediaan — Pemakaian Sendiri & Stok Opname

Qty di 2 baris ini **TIDAK diskalakan** sama sekali (identik di semua tema) — operasional kecil, bukan cerminan volume bisnis.

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 15 | Pemakaian Sendiri | A2×1 dipakai buat sample display etalase toko (Cost Center: **Gudang**) | - | - |
| 18 | Stok Opname | C1: qty sistem dicek, qty fisik = sistem **−1** (ketemu kurang pas hitung fisik, Cost Center: **Gudang**). Mode Periodik: `unit_cost=915rb` wajib diisi manual. | - | - |

### G.5 Aktiva Tetap — 4 jenis transaksi sisanya

Semua lewat form yang sama (**ERP > Accounting > Aktiva Tetap**), field "Jenis Transaksi" beda tiap baris. Simplifikasi: nilai jual/hapus aset diasumsikan pas sama dengan nilai buku (tidak ada gain/loss).

| Tgl | Jenis Transaksi | Akun Debit | Akun Kredit | Nominal |
|---|---|---|---|---|
| 21 | Penyusutan | 6-1400 Beban Penyusutan | 1-2900 Akumulasi Penyusutan | Rp 500.000 |
| 22 | Penghapusan | 1-2900 Akumulasi Penyusutan | 1-2300 Peralatan Kantor | Rp 3.500.000 |
| 24 | Penjualan | 1-1100 Bank | 1-2300 Peralatan Kantor | Rp 5.000.000 |
| 26 | Revaluasi | 1-2300 Peralatan Kantor | 8-1000 Pendapatan Lain-lain | Rp 2.000.000 |

### G.6 Payroll — Pembayaran Sebagian (Partial)

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 28 | Jurnal Umum | Amortisasi sewa tahun 2 bulan 5 (debit 6-1600, kredit 1-1420) | Rp 10.000.000 | - |
| 31 | Payroll - Jurnal Pengakuan | Gaji Mar 2026 (Cost Center: **Operasional**) | Rp 12.032.740 | - |
| 31 | Payroll - Jurnal Pembayaran #1 (sebagian) | Bayar sebagian dulu, sisa Rp 5.032.740 masih hutang | Rp 7.000.000 | **Bank** |
| 31 | Kas Keluar | Listrik + Internet | Rp 2.100.000 | **Kas** |

### April 2026 (1 hari) — Lunasi Sisa Gaji Maret

| Tgl | Dokumen | Detail | Nominal | Bayar |
|---|---|---|---|---|
| 02 | Payroll - Jurnal Pembayaran #2 (pelunasan) | Lunasi sisa gaji Maret 2026 | Rp 5.032.740 | **Bank** |

---

## Checkpoint Interim — Saldo Stok per SKU (per akhir Februari 2026)

Dihitung murni dari total qty masuk dikurangi qty keluar (tidak butuh hitung FIFO manual) — cocokkan dengan field **"Qty On Hand"** di form Product:

| SKU | Total Masuk | Total Keluar | Saldo Akhir |
|---|---|---|---|
| BAN-A1 | 180+150+120 = 450 | 60+48+60+60+48+48+48 = 372 | **78** |
| BAN-A2 | 150+120+120 = 390 | 60+60+60+60 = 240 | **150** |
| BAN-A3 | 120+90+12(retur) = 222 | 48+36 = 84 | **138** |
| BAN-B1 | 180+150 = 330 | 60+36+48+60+36 = 240 | **90** |
| BAN-B2 | 150+120 = 270 | 60+60 = 120 | **150** |
| BAN-B3 | 120+120 = 240 | 48+48 = 96 | **144** |
| BAN-B4 | 120+90 = 210 | 48+48 = 96 | **114** |
| BAN-C1 | 90+90 = 180 | 30+30+36+30 = 126 | **54** |
| BAN-C2 | 90+90 = 180 | 30+36+18+30 = 114 | **66** |

Kalau angka "Qty On Hand" di sistem tidak cocok dengan kolom "Saldo Akhir" di atas, ada transaksi yang salah input/kelewat — cek ulang dari checkpoint bulan terdekat sebelumnya.

## Checkpoint Akhir — Saldo Stok per SKU (per akhir Maret 2026, setelah batch G)

Perubahan dari checkpoint interim di atas, akibat batch Maret 2026 (G.1 Retur Vendor, G.4 Pemakaian Sendiri + Stok Opname, G.2 Delivery C1):

| SKU | Saldo Interim (Feb 2026) | Perubahan Maret | Saldo Akhir |
|---|---|---|---|
| BAN-A1 | 78 | - | **78** |
| BAN-A2 | 150 | −1 (Pemakaian Sendiri) | **149** |
| BAN-A3 | 138 | - | **138** |
| BAN-B1 | 90 | +120 (PO G.1) −12 (Retur Vendor G.1) | **198** |
| BAN-B2 | 150 | - | **150** |
| BAN-B3 | 144 | - | **144** |
| BAN-B4 | 114 | - | **114** |
| BAN-C1 | 54 | −30 (Delivery G.2) −1 (Stok Opname G.4) | **23** |
| BAN-C2 | 66 | - | **66** |

## Checkpoint Piutang/Hutang Outstanding (per akhir Maret/April 2026)

Semua piutang/hutang/uang muka yang dibuat di skenario ini (termasuk batch Maret) sudah **lunas, di-write-off, atau di-apply penuh** — tidak ada Sisa Piutang/Sisa Tagihan yang menggantung, kecuali kalau ada kesalahan input. Perhatikan khusus G.1: setelah Retur Barang Vendor menyebabkan saldo tagihan B1 jadi negatif, **wajib** ada Pembayaran Vendor #3 (refund, nominal negatif) supaya kembali ke 0 — kalau langkah ini kelewat, akan ada Sisa Tagihan minus yang menggantung.

**Catatan**: "2-2000 Hutang Bank Jangka Panjang" dan "2-2100 Hutang Leasing" sengaja **dibiarkan bersaldo** (belum lunas penuh) per akhir skenario — realistis untuk pinjaman jangka panjang, bukan kesalahan input.

## Cakupan Akun

Akun yang **masih** tidak tersentuh (dianggap wajar, di luar scope skenario ini): PPN Masukan/Keluaran & Hutang Pajak (fitur PPN belum dirancang), Tanah/Bangunan/Kendaraan/Aktiva Lain-lain (tidak ada pembelian properti/kendaraan), Laba Tahun Berjalan (by design tidak di-post manual), Dividen, Balancing Account.
