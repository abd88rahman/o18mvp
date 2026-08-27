# app/custom/

Module modifikasi khusus klien, inherit dari [`app/mvp/`](../mvp/) dan/atau [`app/base/`](../base/). **1 klien = 1 repo penuh** — folder ini langsung berisi module custom klien tsb, bukan subfolder per nama klien (beda dari repo referensi `aviat-odoo` yang multi-klien dalam 1 repo).

**Status (2026-08-26): masih kosong** — belum ada klien konkret/kebutuhan modifikasi. Requirement/PRD-nya akan ditulis di [`erd/custom/`](../../erd/custom/) begitu ada kebutuhan nyata.

Folder ini sudah di-mount di [`app/docker/docker-compose.yml`](../docker/docker-compose.yml) (`/mnt/extra-addons/custom`) walau isinya masih kosong.
