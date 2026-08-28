# Rencana (Belum Dibahas): Restriksi Akun per Jenis Jurnal

Status: **ide mentah, sengaja ditunda** — muncul dari diskusi Aktiva Tetap (2026-08-28) tapi user minta jangan dibahas dulu karena melenceng dari topik itu. Dokumen ini cuma nyimpen idenya biar tidak hilang, belum ada keputusan desain final.

## Konteks Munculnya Ide

Waktu bahas guard "harga perolehan Aktiva Tetap wajib cocok dengan Neraca" ([erd/mvp/06-accounting-business.md](../../erd/mvp/06-accounting-business.md) poin G), ketahuan celah: Jurnal Umum (`c18.account.move`, generic, menu "Jurnal Umum") bisa dipakai posting ke akun bertipe **apa saja**, termasuk akun tipe `aktiva_tetap` — padahal harusnya transaksi itu lewat form Aktiva Tetap (`c18.fixed.asset.entry`) supaya laporan Daftar Aktiva Tetap & saldo COA otomatis konsisten (lihat [fixed_asset.py](../../app/mvp/c18_basic_erp/models/fixed_asset.py)).

Opsi "block keras" yang sempat diusulkan: raise `UserError` di `c18.account.move.action_post()` kalau ada line pakai akun tipe `aktiva_tetap`, arahkan user ke form Aktiva Tetap. User setuju arahnya, tapi mau **generalisasi** konsepnya, bukan cuma hardcode 1 kasus (Aktiva Tetap doang).

## 2 Opsi yang Diusulkan User

### Opsi A — Field boolean di CoA
Tambah field di `c18.account.account` (mis. `allow_in_general_journal` atau kebalikannya `restrict_to_dedicated_form`) — akun yang ditandai "tidak boleh" akan ditolak kalau dipakai di Jurnal Umum. Simpel, tapi cuma bisa bedain "boleh di Jurnal Umum" vs "tidak boleh di Jurnal Umum manapun" — tidak granular per jenis jurnal lain.

### Opsi B — Whitelist/blacklist akun per jenis jurnal (lebih luas)
Tiap jenis jurnal (`c18.account.journal` - Jurnal Umum, Jurnal Pengakuan Aktiva, Jurnal Pembelian, dst) punya aturan sendiri akun apa yang **tidak boleh muncul** di pilihan dropdown akun-nya. Contoh yang disebut user: akun **Piutang Usaha** seharusnya tidak boleh muncul dipilih bebas di Jurnal Umum, Jurnal Pengakuan Aktiva, Jurnal Pembelian, dll (karena piutang usaha punya jalur resmi sendiri - lewat Sales Invoice/Sales Receipt).

Ini lebih general & lebih powerful daripada opsi A (bisa atur kombinasi bebas "akun X terlarang di jurnal Y"), tapi juga lebih kompleks — perlu model relasi many-to-many (jurnal ↔ akun terlarang) atau sebaliknya (akun ↔ daftar jurnal yang boleh), plus mekanisme enforce-nya (domain di view + validasi di `action_post`, sama pola kayak yang sudah dipakai buat `debit_account_id` Aktiva Tetap).

## Yang Perlu Diputuskan Nanti
- Opsi A, B, atau kombinasi (A dulu buat MVP, B menyusul kalau ternyata kurang granular)?
- Kalau opsi B: relasi akun↔jurnal itu whitelist (akun cuma boleh di jurnal yang di-list) atau blacklist (akun boleh di semua jurnal KECUALI yang di-list)? Blacklist lebih gampang buat kasus umum ("kebanyakan akun bebas, cuma segelintir yang perlu dibatasi").
- Berlaku dari tier Basic, atau ditunda ke Standard bareng modul-modul yang lebih genuine butuh (Sales/Purchase punya "jalur resmi" sendiri buat piutang/hutang usaha)?
- Cara enforce: block keras (`UserError`) vs cuma warning/notifikasi (pola yang sama dengan diskusi reconciliation Aktiva Tetap sebelumnya)?

## Terkait
- [erd/mvp/06-accounting-business.md](../../erd/mvp/06-accounting-business.md) poin G (Aktiva Tetap Basic) - tempat isu ini pertama muncul.
- [app/mvp/c18_basic_erp/models/fixed_asset.py](../../app/mvp/c18_basic_erp/models/fixed_asset.py) - `_check_coa_reconciliation()`, contoh pola guard yang sudah jalan buat 1 kasus spesifik (Aktiva Tetap), bisa jadi referensi kalau nanti digeneralisasi.
