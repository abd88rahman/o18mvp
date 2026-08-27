# Modul yang Auto-Install di Database Baru (Odoo 18 Community)

Ditelusuri langsung dari source (`odoo/service/db.py` fungsi `_initialize_db`/`exp_create_database`, dan manifest tiap addon di `odoo18_original/addons/`) — bukan tebakan. Relevan untuk jawab: "kalau `docker compose up` lalu bikin database baru tanpa install apa pun manual, modul apa saja yang aktif?"

## Mekanisme
Database baru selalu mulai dari install `base`. Setelah itu, Odoo otomatis meng-install tiap modul lain yang punya `'auto_install': True` di manifest-nya **begitu semua dependency-nya sudah terpenuhi** — ini berantai (modul A auto-install begitu B ter-install, lalu modul C auto-install begitu A ter-install, dst).

## Rantai Auto-Install pada Database Kosong (tanpa install manual apa pun)

```
base
 └─ web              (auto, depends: base)
     ├─ base_setup   (auto, depends: base, web)
     ├─ bus          (auto, depends: base, web)
     ├─ web_tour     (auto, depends: web)
     ├─ base_import  (auto, depends: web)
     ├─ html_editor  (auto, depends: base, bus, web)
     │   └─ web_editor (auto, depends: bus, web, html_editor)
     └─ iap          (auto, depends: web, base_setup)
```

**Total 9 modul**, semuanya infrastruktur murni: `base`, `web`, `base_setup`, `bus`, `web_tour`, `base_import`, `html_editor`, `web_editor`, `iap`.

## Yang TIDAK Auto-Install (mengejutkan, tapi terverifikasi)

| Modul | `auto_install` | `depends` |
|---|---|---|
| `mail` | `False` | `base`, `base_setup`, `bus`, `web_tour`, `html_editor` |
| `portal` | `False` | `web`, `web_editor`, `http_routing`, `mail`, `auth_signup` |
| `contacts` | `False` | `base`, `mail` |
| `auth_signup` | `True`, tapi depends `base_setup`, `mail`, `web` — `mail` belum ada di DB kosong, jadi **tidak ikut ter-trigger** sampai `mail` ter-install duluan oleh sesuatu yang lain |

**Kesimpulan penting**: `mail`, `portal`, `contacts` (Discuss, chatter, app Contacts) **tidak otomatis muncul** di database kosong — baru aktif kalau ada modul lain yang eksplisit depends ke situ (biasanya modul bisnis kayak `sale`/`purchase`, yang justru kita hindari sesuai [erd/00-konvensi-teknis.md](../../erd/00-konvensi-teknis.md) poin 1), atau di-install manual.

`mail` dan `portal` juga **tidak** depends ke `contacts` — jadi ketiganya independen satu sama lain, bukan otomatis ikut-ikutan.

## Implikasi utk Repo Ini

Modul `c18_theme` (`app/base/c18_theme`) punya `'auto_install': ['web']` di manifest — artinya begitu `web` aktif (yang otomatis terjadi di DB manapun), `c18_theme` **juga langsung auto-install**. Karena `c18_theme` sendiri `depends: ['web', 'auth_signup', 'mail', 'portal']`, instalasi `c18_theme` otomatis menarik `mail`+`auth_signup`+`portal` juga (dependency biasa, bukan auto_install listform — tapi karena `c18_theme` butuh semuanya utk bisa ter-install, Odoo akan install semuanya sekaligus sebagai satu paket dependency resolution).

Jadi begitu deployment repo ini bikin database baru: otomatis ter-install = 9 modul infrastruktur di atas + `mail` + `auth_signup` + `portal` + `c18_theme` sendiri. **Belum termasuk `contacts`** (kecuali nanti ada modul `app/mvp` yang eksplisit depends ke situ).

## Cara Verifikasi Jumlah Tabel Pasti
Daftar modul di atas cuma peta "modul mana yang aktif" — untuk **jumlah tabel fisik** yang benar-benar ada di database, jangan hitung dari `grep _name=` di source (bisa salah: ada model abstract/transient tanpa tabel fisik, ada tabel relasi many2many yang muncul otomatis tanpa `_name` eksplisit). Cara paling akurat: setelah `docker compose up` beneran jalan dan database dibuat, query langsung:
```sql
SELECT count(*) FROM information_schema.tables WHERE table_schema='public';
```
