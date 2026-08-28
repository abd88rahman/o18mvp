# testing/

Prosedur testing manual (bukan automated test Odoo) untuk tim tester yang menjalankan smoke test/QA lewat UI browser, ditulis tanpa asumsi background akuntansi. Terpisah dari [`erd/`](../erd/) (requirement) — struktur foldernya sengaja dibuat sejajar per layer (`testing/mvp/` ↔ `erd/mvp/`, dst) supaya gampang dicari.

Tiap dokumen berisi: setup data master, skenario bernomor dengan langkah persis + hasil yang diharapkan, dan checklist ringkasan di akhir buat direkap hasil.

## Konvensi Penomoran per Folder Modul

Kalau ada beberapa dokumen saling terkait dalam 1 skenario/cerita, dinomori berurutan (pola sama seperti `erd/`):
- `00-*` — profil/parameter skenario (perusahaan, harga, asumsi) — bacaan pertama, jarang berubah.
- `01-*`, `02-*`, dst — turunannya (data transaksi detail, prosedur eksekusi UI) — makin besar nomor, makin operasional/sering dipakai ulang.

Contoh: [`mvp/00-skenario-distributor-ban.md`](mvp/00-skenario-distributor-ban.md) (profil PT Roda Sejahtera) → [`mvp/01-transaksi-distributor-ban.md`](mvp/01-transaksi-distributor-ban.md) (data transaksi Nov 2024-Feb 2026) → [`mvp/02-prosedur-testing.md`](mvp/02-prosedur-testing.md) (cara eksekusinya di UI).
