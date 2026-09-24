# Setting Nginx + Certbot untuk Multi-Domain (Beberapa Container Odoo di 1 Server)

Jawaban atas [`../human-notes/cara setting nginx.txt`](../human-notes/cara%20setting%20nginx.txt): server cloud sudah jalan, rencana beberapa container docker, domain sudah ada:
- `sub1.domain.id` → odoo1 (repo ini, `o18mvp`)
- `sub2.domain.id` → odoo2 (repo lain, **belum dibuat**)

## Status Saat Ini (2026-08-29)

**Sudah selesai untuk `sub1.domain.id`** (odoo1, repo ini) — nginx host + SSL certbot sudah terpasang dan jalan, langkah 1-5 di bawah sudah dieksekusi semua di server:
- nginx & certbot ter-install, service nginx `active (running)`.
- Server block dibuat di `sites-available`, di-symlink ke `sites-enabled`, `nginx -t` sukses.
- SSL terpasang via `certbot --nginx -d sub1.domain.id`.
- `certbot.timer` aktif untuk auto-renew, `certbot renew --dry-run` sukses.

Kendala yang ditemukan & solusinya (dicatat untuk referensi kalau ulang di server lain): `nginx -t` sempat gagal dengan error `socket() [::]:80 failed (97: Address family not supported by protocol)` — penyebabnya baris `listen [::]:80 default_server;` di `sites-enabled/default` (server ini tidak mendukung IPv6). Solusi: hapus symlink `sites-enabled/default` (`sudo rm /etc/nginx/sites-enabled/default`). Juga sempat `systemctl reload nginx` gagal karena nginx belum pernah di-`start` — servicenya perlu `sudo systemctl start nginx` dulu (bukan reload) untuk instalasi baru.

**Susulan (2026-08-31)**: `413 Request Entity Too Large` saat restore database (3MB) lewat Database Manager — server block awal tidak punya `client_max_body_size` (default nginx cuma 1MB). File `sites-available/sub1.domain.id` di server WAJIB ditambah manual (bukan otomatis kebawa dari repo, krn file ini dibuat langsung di server lewat heredoc, bukan disalin dari `app/docker/nginx/odoo-erp.conf`):
```bash
sudo nano /etc/nginx/sites-available/sub1.domain.id
# tambah baris "client_max_body_size 500M;" di dalam blok server { ... }
# (kalau sudah ada blok listen 443 ssl dari certbot, tambahkan di SEMUA blok server yang ada)
sudo nginx -t
sudo systemctl reload nginx
```
Template repo (`app/docker/nginx/odoo-erp.conf`) dan langkah 2 di atas sudah diupdate ikut sertakan baris ini, supaya domain berikutnya (odoo2 dst) tidak kena masalah yang sama.

**Belum dikerjakan**: cek ulang `docker compose ps` di `app/docker/` repo ini untuk pastikan service `nginx` (profile `proxy`) tidak ikut jalan (supaya tidak bentrok port 80 dengan nginx host).

Bagian "Referensi Multi-Domain" di bawahnya baru relevan **nanti** kalau odoo2 (atau repo lain) sudah dibuat dan mau digabung ke server yang sama.

## Langkah Sekarang: Setup `sub1.domain.id` (1 Domain)

### 1. Install nginx + certbot
```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
sudo ufw allow 'Nginx Full'
```

### 2. Buat file server block
```bash
sudo tee /etc/nginx/sites-available/sub1.domain.id > /dev/null <<'EOF'
upstream odoo1_backend {
    server 127.0.0.1:8069;
}
upstream odoo1_longpolling {
    server 127.0.0.1:8072;
}

server {
    listen 80;
    server_name sub1.domain.id;

    # Default nginx cuma 1MB - kekecilan utk restore database (Database
    # Manager) atau upload attachment besar. 500M cukup longgar.
    client_max_body_size 500M;

    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;

    proxy_set_header X-Forwarded-Host $host;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header X-Real-IP $remote_addr;

    location /websocket {
        proxy_pass http://odoo1_longpolling;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        proxy_pass http://odoo1_backend;
    }
}
EOF
```
Ganti `sub1.domain.id` di dalam file (baris `server_name` dan nama file-nya) dengan domain asli. Perintah `sudo tee ... > /dev/null <<'EOF' ... EOF` menulis file langsung dari command line tanpa buka editor — tanda kutip di `'EOF'` penting supaya `$host` dkk tidak dianggap variabel shell, dibiarkan literal untuk dibaca nginx.

### 3. Aktifkan & reload
```bash
sudo ln -s /etc/nginx/sites-available/sub1.domain.id /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```
Pastikan DNS A record domain sudah mengarah ke IP server ini sebelum lanjut ke langkah SSL.

### 4. Pasang SSL
```bash
sudo certbot --nginx -d sub1.domain.id
```
Ikuti prompt (email, setuju ToS). Certbot otomatis nambahin blok `listen 443 ssl;` + redirect HTTP→HTTPS ke file `sites-available/sub1.domain.id`.

### 5. Cek auto-renew
```bash
sudo systemctl status certbot.timer
sudo certbot renew --dry-run
```
Package `certbot` di Ubuntu/Debian sudah otomatis pasang systemd timer, tidak perlu cron manual.

### 6. Jangan lupa
- **Jangan** jalankan `docker compose --profile proxy up -d` di repo ini — nginx host yang sekarang pegang port 80/443, bukan container nginx bawaan repo.
- Port Odoo (8069/8072) tetap ter-expose ke `0.0.0.0` lewat `docker-compose.yml` saat ini. Kalau semua akses publik sudah lewat nginx host, pertimbangkan ubah jadi `"127.0.0.1:8069:8069"` dst supaya port itu tidak bisa diakses langsung dari internet.

---

## Referensi Multi-Domain (Untuk Nanti, Saat odoo2 Sudah Ada)

Bagian di bawah ini pola yang sama, digeneralisasi untuk kondisi 2+ container Odoo di 1 server.

### Kenapa Bukan Pakai Service `nginx` di `docker-compose.yml` Repo Ini

Repo ini sudah punya service `nginx` (profile `proxy`, lihat [`app/docker/docker-compose.yml`](../../app/docker/docker-compose.yml) dan [`app/docker/nginx/README-nginx-erp-url.md`](../../app/docker/nginx/README-nginx-erp-url.md)) — tapi itu untuk rewrite path `/odoo` → `/erp` di **satu** instance, dan dia bind port `80:80` di host.

Kalau tiap repo (odoo1, odoo2, ...) punya container nginx sendiri yang sama-sama mau pakai port 80/443 di host, **bentrok** — cuma satu yang bisa menang. Jadi untuk multi-domain, pola yang dipakai adalah:

- **Satu nginx di level host** (install langsung di server, bukan di dalam Docker) sebagai pintu masuk tunggal untuk port 80/443.
- Tiap container Odoo cukup expose port ke host di port yang **beda-beda** (tidak dipakai bareng).
- Nginx host yang route berdasarkan `server_name` (subdomain) ke port host masing-masing.
- Certbot jalan di host, terintegrasi ke nginx host itu.

**Jangan jalankan `docker compose --profile proxy up -d` di repo ini** kalau pakai pola ini — cukup service `db` dan `odoo18-erp` saja, port Odoo tetap di-expose ke host seperti sudah ada di compose file.

## 1. Alokasi Port per Repo

Odoo pakai 2 port: HTTP utama (8069) dan longpolling/websocket (8072). Kalau beberapa container jalan di host yang sama, port-nya harus unik per repo. Contoh:

| Repo / Subdomain      | Port HTTP (host) | Port Longpolling (host) |
|------------------------|-------------------|---------------------------|
| odoo1 / `sub1.domain.id` | 8069              | 8072                      |
| odoo2 / `sub2.domain.id` | 8169              | 8172                      |
| odoo3 / `sub3.domain.id` (kalau nanti ada) | 8269 | 8272 |

Repo ini (`o18mvp`) sudah pakai 8069/8072 secara default (lihat `app/docker/docker-compose.yml` baris `ports:`) — biarkan saja. Untuk repo odoo2, di `docker-compose.yml` repo itu ubah baris `ports:` jadi:

```yaml
ports:
  - "8169:8069"
  - "8172:8072"
```

(Angka kiri = port host yang unik, angka kanan = port di dalam container, tetap 8069/8072 karena itu port default Odoo.)

## 2. Untuk odoo2: Ulangi Langkah 1-5 di Bagian "Langkah Sekarang", dengan Penyesuaian

Ikuti persis langkah 1-5 di bagian atas, tinggal ganti:
- nama file & `server_name` → `sub2.domain.id`
- nama upstream → `odoo2_backend` / `odoo2_longpolling` (biar tidak bentrok nama antar file)
- port upstream → `8169` dan `8172` (bukan `8069`/`8072`)
- `certbot --nginx -d sub2.domain.id`

> Kalau repo odoo2 butuh rewrite `/odoo` → `/erp` juga seperti draft di [`odoo-erp.conf`](../../app/docker/nginx/odoo-erp.conf) repo ini, tinggal contek pola `location /erp { rewrite ... proxy_pass ...; proxy_redirect ...; }` dari file itu, ditaruh di server block host ini — bukan lewat container nginx repo.

## Ringkasan Alur

```
Internet (port 80/443)
        │
        ▼
  nginx (host, native install)  ──certbot──> SSL per subdomain
        │
        ├── server_name sub1.domain.id ──> 127.0.0.1:8069 (odoo1, repo ini)
        └── server_name sub2.domain.id ──> 127.0.0.1:8169 (odoo2, repo lain)
```

Container `nginx` bawaan repo ini (profile `proxy`) tidak dipakai di pola ini — biarkan mati kalau host sudah punya nginx sendiri di depan.

## Catatan Keamanan
- Jangan commit sertifikat (`.pem`/`.key`) atau apa pun dari `/etc/letsencrypt/` ke repo manapun.
- Kalau port Odoo (8069/8072 dst) tidak perlu diakses langsung dari luar (semua akses lewat nginx), pertimbangkan bind ke `127.0.0.1` saja di `docker-compose.yml`, misal `"127.0.0.1:8069:8069"` — supaya port itu tidak bisa diakses langsung dari internet, cuma lewat nginx.
