# Requirement - QA Guide Viewer (`c18_help`)

Status: **permanen** (diputuskan 2026-08-30, sebelumnya prototype/spike tanpa requirement resmi). PRD ini ditulis belakangan (setelah modul ada), bukan sebelum — mendokumentasikan keputusan yang sudah diambil, bukan requirement awal.

## Latar Belakang

Skenario testing "PT Roda Sejahtera" (`testing/mvp/00-skenario-distributor-ban.md`, `01-transaksi-distributor-ban.md`, `02-prosedur-testing.md`) ditulis untuk dieksekusi manual lewat UI Odoo oleh tester. Awalnya tester harus buka file `.md` di editor/GitHub terpisah dari aplikasi. `c18_help` dibuat supaya tester bisa baca prosedur **di dalam Odoo itu sendiri** (menu "QA Guide"), sambil buka menu lain (Kas Bank, PO, dst) untuk eksekusi — tidak perlu alt-tab keluar aplikasi.

## Audiens & Batasan — WAJIB Dipahami

**Modul ini untuk tester/QA internal, BUKAN untuk client/end-user.** Ini bukan sekadar preferensi, tapi konsekuensi langsung dari isi kontennya:
- Bahasa & istilahnya testing/verifikasi ("Hasil yang Diharapkan", checkpoint saldo akun, referensi ke dokumen requirement internal).
- Skenarionya perusahaan fiktif "PT Roda Sejahtera" — dibuat buat menguji fitur, bukan representasi bisnis client asli.
- Kalau nanti ada kebutuhan tutorial untuk client sungguhan, itu **modul/folder terpisah** ([docs/user-guide/](../../docs/user-guide/), masih kosong per 2026-08-30) — bukan menambah isi di `c18_help` yang sudah ada.

**Konsekuensi teknis**: modul ini **tidak boleh ter-install di database demo atau database yang diakses client**. Saat ini tidak ada pembatasan hak akses (`ir.model.access.csv` cuma atur CRUD, bukan visibility per role) — satu-satunya pengaman adalah **tidak menginstall modul ini** di database yang bakal dilihat pihak luar. Ini murni disiplin operasional (cek manual saat provisioning database demo/client), bukan sesuatu yang dijamin otomatis oleh kode.

## Keputusan Desain

| Keputusan | Alasan |
|---|---|
| `'auto_install'` **tidak diset** (default `False`) | Beda dari `c18_basic_erp` yang auto-install — modul ini harus sengaja diinstall, bukan otomatis nempel di setiap deployment (termasuk yang berpotensi jadi demo/client). |
| `category: 'Hidden'` | Tidak muncul di Apps biasa tanpa developer mode — mengurangi risiko ter-install tidak sengaja. |
| Root menu top-level, TIDAK direparent ke `c18_theme.menu_erp_root` | Beda karakter dari module bisnis (Sales/Purchase/Accounting) — ini utility/dokumentasi, bukan bagian workflow ERP inti. |
| Label menu **"QA Guide"** (bukan "Help" generik) | Diubah 2026-08-30 — nama "Help" ambigu, berisiko disangka menu untuk semua orang (termasuk client) kalau ada yang lihat sekilas. |
| Nama teknis (`c18_help`, model `c18.help.guide`, folder) **TIDAK** ikut di-rename | Keputusan 2026-08-30 — cukup label UI yang diubah, rename teknis dianggap kerja lebih besar (migrasi folder/xmlid) tanpa manfaat langsung buat tujuan "bedakan internal vs client". |
| Render `.rst` → HTML on-the-fly, tidak ada file HTML perantara tersimpan | Konten selalu fresh dari file sumber tiap form dibuka — tidak ada risiko cache HTML basi. |

## Cara Kerja Teknis
Lihat komentar di [`models/guide.py`](../../app/base/c18_help/models/guide.py) — `c18.help.guide` (1 record per dokumen) punya field `filename` (path relatif ke `static/docs/*.rst`) dan `content` (computed `Html`, baca file & convert pakai `docutils.core.publish_parts`, `report_level=5` supaya warning minor RST tidak jadi exception).

## Cara Sinkronisasi `.rst`

**File `.rst` di `static/docs/` adalah salinan, BUKAN sumber asli** — sumber aslinya `testing/mvp/*.md`. Tidak ada mekanisme otomatis (tidak ada CI/hook) yang menjaga keduanya tetap sinkron — kalau `.md` sumber diupdate, `.rst` **HARUS** disinkronkan manual, kalau tidak, isi yang tampil di UI Odoo jadi basi (kejadian nyata 2026-08-30 — `.rst` sempat ketinggalan setelah `.md` diupdate soal Tutup Buku 2025).

Prosedur sinkronisasi (dipraktikkan 2026-08-30, pakai `pandoc`):
```bash
pandoc -f markdown -t rst testing/mvp/00-skenario-distributor-ban.md -o /tmp/00.rst
# ulangi utk 01 & 02, lalu bersihkan link markdown antar-dokumen (jadi dead-link
# di RST karena bukan file terpisah di context Odoo) - regex:
# `([^`<]+?)\s*<[^>]+?\.md>`__?  ->  \1
# lalu copy ke app/base/c18_help/static/docs/, verifikasi lewat docutils.core.publish_parts
```
**Belum ada otomasi** untuk ini (mis. hook pre-commit atau script) — kalau makin sering out-of-sync, pertimbangkan bikin script pembantu, tapi belum jadi kebutuhan mendesak per 2026-08-30 (baru sinkron manual 1x).

## Status Implementasi
Sudah di-scaffold penuh, 3 dokumen sudah sinkron dengan sumber `.md` per 2026-08-30. Belum ada test otomatis (functional test-nya cukup: install modul + panggil `_render_rst()` tiap record, tidak exception — sudah diverifikasi manual).

## Belum Dikerjakan (Kandidat ke Depan, Bukan Blocker)
- Pembatasan hak akses eksplisit (mis. security group khusus tester) — saat ini murni disiplin "jangan install di db client", bukan dijamin sistem.
- Otomasi sinkronisasi `.rst` (script/hook).
- Icon custom untuk menu root (masih default).
