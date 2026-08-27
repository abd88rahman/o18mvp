# Titik Akhir Sesi Ini (2026-08-26, sesi lanjutan)

## Kalimat Penutup Sesi
> (menunggu instruksi lanjutan dari user — sesi ini murni rincian `06-accounting-business.md` tier Basic, belum ada pertanyaan terbuka spesifik di akhir)

## Ringkasan Progres Sesi Ini
Fokus sesi ini: merinci gap "Detail requirement Basic tier" di `erd/00-tiering-produk.md` sampai tuntas, khusus modul `c18_account` (Accounting). Hasilnya jadi section besar baru **"Detail Requirement Tier Basic — Field-Level"** di [`erd/mvp/06-accounting-business.md`](../../erd/mvp/06-accounting-business.md), poin **A sampai K**:

- **A.** Jurnal Umum (form spesifik).
- **B.** Kas Bank — 3 form (Kas Masuk/Keluar pakai `line_ids`, Transfer flat).
- **C.** Tutup Buku (baru, diriset dari pola Accurate Online) — Penyesuaian Awal Tahun (locked 1 Jan), Penyesuaian Akhir Tahun (locked 31 Des), Tutup Buku/closing entries (nolkan P&L langsung ke Laba Ditahan, bukan via Income Summary). Termasuk penjelasan dampak ke Laporan Laba Rugi (harus exclude jurnal penutup) vs Neraca (Laba Tahun Berjalan tetap tampil kalau tanggal laporan < tutup buku).
- **D. Pembelian** — termasuk **PO ringan** (keputusan besar sesi ini: Basic ternyata butuh PO versi ringan + Product versi sederhana, bukan "tidak ada Purchase sama sekali" seperti draft awal — dikonfirmasi setelah diskusi pro-kontra, dianalogikan beda dari register Aktiva Tetap yang justru ditiadakan). 6 jenis jurnal dirinci lengkap: Penerimaan Barang, Pembelian (GRNI fleksibel + `product_id`/keterangan bebas per baris), Uang Muka Pembelian, Pembayaran Vendor (line_ids pilih invoice + wizard deduction multi-baris), Retur Barang Vendor (diriset: retur selalu sama caranya, status bayar cuma pengaruh follow-up lewat Pembayaran Vendor nominal negatif), Write-off Hutang (diriset maknanya: cuma utk hutang yang genuinely dibebaskan/gain, beda dari pelunasan non-kas yang masuk perluasan Pembayaran Vendor).
- **E. Penjualan** — mirror penuh dari D, dengan 1 asimetri kunci: tidak ada akun perantara "Piutang Belum Difaktur" (Pengiriman Barang langsung akui HPP, bukan piutang).
- **F. Persediaan** — mekanisme costing FIFO/Average (dipilih per company), penyimpanan (layer table utk FIFO, running qty+avg_cost utk Average), efek tiap mutasi, larangan stok negatif, laporan (Kartu Stok + Saldo Persediaan; Stok Minimum & per-Gudang dikonfirmasi TIDAK perlu). **F.1** Pemakaian Sendiri (Consume, jenis jurnal baru) dan **F.2** Stok Opname (jenis jurnal baru) — keduanya di luar 6+6 jenis resmi `tiering-versi.txt`.
- **G.** Aktiva Tetap Basic — tanpa register aset (sengaja ditiadakan, alasan "kesan setengah jadi").
- **H.** Payroll Basic — 2 jenis jurnal, relasi Pengakuan↔Pembayaran via pull (pilih di form Pembayaran) + push (tombol "Bayar" di form Pengakuan).
- **I.** Partner Basic — field minimal.
- **J.** Product/UoM di Basic — Product dipakai (versi sederhana: kode bebas format + tipe + is_purchaseable/is_saleable, TANPA UoM/kategori model), UoM tetap Standard+ saja.
- **K.** Skema Nomor Dokumen — placeholder `ir.sequence` sudah **dibuat filenya** di [`app/mvp/c18_account/data/ir_sequence_data.xml`](../../app/mvp/c18_account/data/ir_sequence_data.xml) (~27 sequence, format `KODE-yyyy-mm-xxx`, kode prefix ≤4 huruf, `no_gap`) — belum terdaftar ke manifest krn module `c18_account` belum discaffold.

## Dokumen Lain yang Ikut Diupdate
- `erd/00-tiering-produk.md` — breakdown Basic dikoreksi (PO ringan + Product masuk Basic), tabel pemetaan tier diupdate.
- `erd/mvp/02-common-master-data.md` — Product sekarang tier "semua tier" (bukan Standard+ saja), field level Basic dirinci, kode prefix **dikonfirmasi bebas karakter** (tidak divalidasi sistem).
- `erd/mvp/04-purchase.md` — dicatat PO ringan sudah ada di Basic (`c18_account`), `c18_purchase` nanti `_inherit` model itu.
- `erd/mvp/01-accounting-foundation.md` — **item "Belum Diputuskan" (sub-kategori 15 tipe akun) sudah diselesaikan**: tabel 41 baris (No, Kode & Nama Akun, Tipe Akun, Default Fitur?, Fitur Pemakai). Skema kode: segmen pertama = tipe (1 Aktiva, 2 Kewajiban, 3 Ekuitas, 4 Pendapatan, 5 Beban Pokok, 6 Beban Usaha, 8 Pendapatan di Luar Usaha, 9 Beban di Luar Usaha — **tidak ada prefix 7**, dikoreksi user), segmen kedua kelipatan 100.

## Keputusan Besar yang Perlu Diingat
1. **PO ringan + Product ada di Basic** (bukan Standard+) — keduanya tetap hidup di modul `c18_account` (bukan dipindah ke `c18_common`), supaya Basic cukup install 1 modul. Trade-off: `c18_account` jadi tidak murni "GL doang".
2. **Metode costing (FIFO/Average) dipilih per company** (global, bukan per produk).
3. **Stok negatif tidak diperbolehkan** — validasi wajib sebelum posting.
4. **Laporan Stok Minimum dikonfirmasi TIDAK diperlukan** di MVP ini sama sekali.

## Belum Dikerjakan / Masih Terbuka (Kandidat Sesi Berikutnya)
- [ ] Field aging/umur hutang-piutang (bantu identifikasi kandidat Write-off) — dicatat sbg follow-up, belum wajib.
>jawab: tidak perlu, skip saja
- [ ] Format Kartu Stok (kolom/layout persis) — isi sudah jelas, layout belum.
>jawab: buatkan layout yaa
- [ ] Finalisasi skema nomor dokumen poin K (apakah `no_gap` sudah benar, apakah reset per bulan yang diinginkan) — placeholder XML sudah ada, tinggal dikonfirmasi/direvisi.
>jawab: nomor berlanjut seterusnya karna tier basic memang simple
- [ ] Riset 3 repo referensi payroll (`odoo18-toso`, `odoo18-cep`, `odoo10-kp3`) utk `07-hris.md` — **masih menggantung dari sesi sebelumnya**, belum disentuh sesi ini.
>jawab: masih open
- [ ] Rinci **05-sales.md** & **04-purchase.md** (Standard+) — masih level tinggi, belum sedetail Basic tier di `06`.
>jawab: masih open
- [ ] Smoke test `c18_theme` + `app/docker/` ke instance Odoo sungguhan — masih menggantung dari sesi-sesi sebelumnya, belum pernah dijalankan sama sekali.
>jawab: masih open
- [ ] Mulai scaffold kode modul `c18_account` — requirement Basic sudah sangat lengkap sekarang, tinggal mulai coding.
>jawab: masih open

## Peta Dokumen Penting (update dari sesi sebelumnya)
- `erd/mvp/06-accounting-business.md` — sekarang dokumen PALING detail & PALING panjang, jadi rujukan utama field-level utk `c18_account`.
- `erd/mvp/01-accounting-foundation.md` — tabel CoA 41 akun + kode sudah lengkap.
- `app/mvp/c18_account/data/ir_sequence_data.xml` — **file kode pertama** yang sudah dibuat di `app/mvp/` (masih orphan, belum ada manifest/module).
- Dokumen lain (`00-tiering-produk.md`, `02-common-master-data.md`, `04-purchase.md`) — sudah konsisten dengan keputusan sesi ini.
