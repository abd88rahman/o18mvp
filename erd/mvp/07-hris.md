# Requirement - HRIS & Payroll (`c18_hris`)

Status: **draft direview sebagian (2026-08-26), belum diimplementasikan.** Riset ke repo referensi payroll masih perlu dilakukan sebelum model final ditulis detail.

**Tier: Enterprise** (kustomisasi) — lihat [erd/00-tiering-produk.md](../00-tiering-produk.md). Bukan bagian Basic maupun Standard. **Tapi tetap bagian MVP inti** (bukan full-custom per klien) — HRIS versi MVP ini fiturnya sederhana/baseline, kustomisasi lebih lanjut sesuai kebutuhan klien spesifik baru masuk `app/custom`.

## Posisi dalam Alur
Beda karakter dari Sales/Purchase/Inventory — HRIS relatif berdiri sendiri, tapi ujungnya tetap depends ke [`c18_account`](01-accounting-foundation.md) (jurnal Hutang Gaji, Bayar Gaji sudah didaftar di [01](01-accounting-foundation.md#2-journal--c18accountjournal)) dan Cost Center (alokasi biaya gaji ke departemen/project — **dikonfirmasi** dipakai dari awal).

Sesuai [erd/00-konvensi-teknis.md](../00-konvensi-teknis.md): zero dependency ke `hr`/`hr_contract`/`hr_payroll` bawaan Odoo — model dibangun dari nol. **Catatan penting**: `hr_payroll` itu sendiri **Enterprise-only** (tidak ada di Community sama sekali — lihat [notes/claude-notes/daftar-modul-odoo18-community.md](../../notes/claude-notes/daftar-modul-odoo18-community.md)), jadi zero-dependency di sini bukan pilihan, memang satu-satunya jalan.

Nama modul final: **`c18_hris`** — **1 modul gabungan** (data karyawan + payroll jadi satu, tidak dipecah `c18_hr`/`c18_hr_payroll` terpisah).

`master-plan.txt` menyediakan **3 referensi khusus payroll**: `odoo18-toso` (base/theme/payroll), `odoo18-cep` (payroll, compare dg toso), `odoo10-kp3` (payroll, alternatif) — **masih perlu diriset** ke repo-repo ini sebelum detail model (salary rule, PPh 21, BPJS) difinalkan.

## Scope

### 1. Data Karyawan
- `c18.hr.employee` — data karyawan (NIK, NPWP, status BPJS, dsb). **Tidak** extend `res.partner` (beda kasus dari Partner di [02](02-common-master-data.md) — karyawan bukan customer/vendor, `hr.employee` juga bukan bagian `base`, jadi tetap model baru).
- Department, Job Position.

### 2. Kontrak Kerja
- `c18.hr.contract` — kontrak kerja (tunjangan tetap/tidak tetap, upah pokok).
- **Riwayat nilai kontrak dibutuhkan** — histori perubahan gaji bertanggal (bukan edit langsung/duplikasi kontrak tiap kenaikan gaji), mirip konsep yang pernah ditemukan di proyek referensi lain (`hr.contract.revision`-style).

### 3. Attendance & Time Off (Cuti/Izin)
**Masuk MVP awal, versi sederhana** — meskipun HRIS ini tier Enterprise, tetap bagian MVP inti (bukan full-custom). Fitur lanjutan/spesifik per klien menyusul di `app/custom`, bukan di modul MVP ini.

### 4. Payroll
- Struktur gaji & **salary rule sebagai data master** — fleksibel, bisa nambah rule baru tanpa ubah kode (bukan hardcode).
- **PPh 21** — kemungkinan pakai metode TER (Tarif Efektif Rata-rata, mandatory sejak PMK 168/2023), perlu dipastikan lagi ke referensi.
- **BPJS** — Kesehatan & Ketenagakerjaan (JHT/JP/JKK/JKM), dengan batas atas/bawah dasar iuran yang berubah dari waktu ke waktu (master data bertanggal, bukan angka statis). **Perlu juga tabel master UMK (Upah Minimum Kota/Kabupaten)** sebagai batas bawah dasar iuran per daerah.
- Payslip (slip gaji) + Payslip Batch/Run (proses banyak karyawan sekaligus).
- **Biaya gaji dialokasikan ke Cost Center** (departemen/project) — dikonfirmasi dari awal, bukan ditunda.
- Payslip Batch → jurnal Hutang Gaji → Bayar Gaji.

## Belum Diputuskan / Perlu Digali
- [ ] **Riset ke 3 repo referensi payroll** (`odoo18-toso`, `odoo18-cep`, `odoo10-kp3`) — bandingkan pendekatan masing-masing (salary rule, PPh 21 TER, BPJS) sebelum detail model difinalkan.
