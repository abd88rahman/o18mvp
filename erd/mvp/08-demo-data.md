# Demo Data untuk Presentasi Client (`c18_basic_erp`)

Status: **selesai & terverifikasi** (2026-08-30). Ditulis setelah implementasi (bukan requirement awal) — mendokumentasikan keputusan & keterbatasan teknis yang ditemukan saat dikerjakan.

## Tujuan
Dataset ringkas (~13 transaksi) buat presentasi ke calon client — supaya form-form kunci (Kas Bank, siklus Pembelian, siklus Penjualan, Aktiva Tetap, Payroll) sudah terisi contoh begitu database baru dibuat, tidak perlu isi manual dulu di depan client. **Bukan** pengganti skenario testing lengkap di `testing/mvp/*.md` (itu untuk QA internal 16+ bulan, lihat [`erd/base/06-qa-guide-viewer.md`](../base/06-qa-guide-viewer.md)) — demo data ini scope-nya jauh lebih kecil & tanggalnya relatif ke hari generate, bukan histori multi-tahun.

## Keterbatasan Teknis Ditemukan — Mekanisme 'demo' Odoo TIDAK BISA Dipakai

Rencana awal: pakai mekanisme demo data bawaan Odoo (key `'demo'` di manifest, load otomatis kalau user centang "Demo Data" saat create database). **Ini tidak bisa dipakai untuk `c18_basic_erp`**, dibuktikan lewat testing langsung (2 database berbeda, hasil konsisten) + cross-check ke source Odoo (`odoo/modules/graph.py` method `should_have_demo`, `odoo/tools/config.py` baris 570-571):

- `c18_basic_erp` punya `'auto_install': True` (wajib, desain sengaja — lihat [01-accounting-foundation.md](01-accounting-foundation.md)/manifest, supaya otomatis aktif begitu `c18_theme` terinstall).
- `config['demo']` di Odoo diisi = **copy persis** dari `config['init']` (daftar modul yang eksplisit diminta lewat `-i`) — bukan `{'all': True}` seperti dugaan awal.
- Modul yang masuk graph lewat jalur **auto_install** (bukan diminta eksplisit lewat `-i`) tidak pernah tercatat di `config['demo']`, jadi flag `demo` node-nya di graph resolution selalu `False` — **walaupun** modul itu juga diketik eksplisit di `-i` bersamaan dengan parent-nya (sudah dicoba, hasilnya tetap `False`).
- Ini murni keterbatasan/quirk Odoo sendiri terkait interaksi `auto_install` + resolusi graph demo, bukan bug di kode kita, dan tidak ada workaround praktis selain tidak mengandalkan mekanisme ini.

**Keputusan**: `c18_basic_erp` tetap `auto_install: True` (tidak diubah demi demo data — itu prioritas lebih rendah dari desain instalasi utama). Demo data di-generate **manual**, bukan lewat checkbox.

## Cara Pakai

Lewat `odoo shell`:
```python
env['c18.basic.erp.demo.generator']._generate()
env.cr.commit()
```

**Idempotent** — aman dipanggil ulang (mis. lupa sudah pernah generate), tidak akan membuat data dobel. Dijaga lewat `ir.config_parameter` (`c18_basic_erp.demo_generated`) — begitu sekali berhasil, panggilan berikutnya langsung `return` tanpa efek apa pun.

## Isi Dataset (~13 dokumen, 10 jurnal akuntansi ter-posting)
Tanggal semuanya **relatif ke hari `_generate()` dipanggil** (`today - N hari`), bukan tanggal fixed — supaya masuk akal kapan pun demo di-generate:

1. Kas Masuk — pendapatan lain-lain (sewa gudang).
2. Kas Keluar — beli ATK.
3. Transfer Kas → Bank.
4-6. Siklus Pembelian: PO (vendor "PT Ban Nusantara Distribusi", 20 unit) → Penerimaan Barang → Pembelian (Vendor Bill, via GRNI).
7-9. Siklus Penjualan: SO (customer "Toko Ban Makmur", 10 unit) → Delivery (FIFO costing) → Customer Invoice.
10. Aktiva Tetap — Acquisition (printer kantor, dibayar tunai dari Bank).
11-12. Payroll — Accrual + Payment penuh (karyawan "Budi Santoso").

**Sengaja TIDAK termasuk**: Tutup Buku (Period Closing) — beresiko mengunci periode kalau demo db di-reset/reload berkali-kali, dan bukan hal utama yang perlu ditunjukkan ke client di presentasi awal.

## Lokasi Kode
- Logic generator: [`app/mvp/c18_basic_erp/models/demo_generator.py`](../../app/mvp/c18_basic_erp/models/demo_generator.py) — `TransientModel` `c18.basic.erp.demo.generator`, method `_generate()`. Python (bukan `<record>` XML statis) karena tiap transaksi butuh `action_post()` supaya jurnal akuntansi beneran ter-generate (efek sampingnya: update stok FIFO, generate `c18.account.move`, dst) — data mentah lewat XML `<record>` saja tidak memicu logic itu.

## Diverifikasi
Dijalankan 2x ke database test terpisah (`demo-test2`, bukan database kerja) — run pertama sempat gagal (bug di kode: `c18.payroll.payment.account_id` wajib diisi tapi generator awalnya andalkan `action_pay()` yang tidak mengisi field itu, sudah diperbaiki jadi create manual langsung isi `account_id`), run kedua sukses penuh: 13 dokumen posted, 10 jurnal, stok produk BAN-A1 = 10 unit (20 diterima − 10 dikirim, sesuai perhitungan). Panggilan ulang ke-2 (test idempotency) — tidak ada data dobel.
