#!/bin/bash
set -e

echo -e "\n--- pull dari repo ---"
cd "o18mvp/app/docker"
git pull
echo -e "\n--- sudah pull ---"

echo -e "\n--- restart docker ---"
docker compose -f docker-compose.yml --progress plain restart

echo -e "\n--- status ---"
docker compose -f docker-compose.yml ps

echo -e "\n--- done ---"