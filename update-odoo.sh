#!/bin/bash
set -e

echo -e "\n--- pull dari repo ---"
cd "$(dirname "$0")/app/docker"
git pull
echo -e "\n--- sudah pull ---"

echo -e "\n--- apply docker-compose ---"
# up -d (bukan restart): restart tidak menerapkan perubahan docker-compose.yml
# dan tidak menjalankan odoo18-erp-init.
docker compose -f docker-compose.yml --progress plain up -d

echo -e "\n--- restart odoo (muat ulang kode modul) ---"
docker compose -f docker-compose.yml --progress plain restart odoo18-erp

echo -e "\n--- status ---"
docker compose -f docker-compose.yml ps

echo -e "\n--- done ---"