#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if ! command -v docker >/dev/null 2>&1; then
  echo "Install Docker Desktop, start it, then run this launcher again." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running. Open Docker Desktop and wait until its engine is ready." >&2
  exit 1
fi
docker compose version >/dev/null
if [ ! -f .env ]; then cp .env.example .env; fi
echo "Building and starting BidFit on your computer. First run needs internet and may take several minutes."
docker compose --env-file .env -f compose.local.yml up --build -d --wait --wait-timeout 240
docker compose --env-file .env -f compose.local.yml exec -T api python infra/seed_demo.py
address="$(docker compose --env-file .env -f compose.local.yml port api 8000)"
echo "BidFit is ready on your computer: http://${address}"
echo "Use Alice's local demo login. Open the Example project or create a new one."
echo "Stop later with: docker compose --env-file .env -f compose.local.yml down"
if command -v open >/dev/null 2>&1; then
  open "http://${address}"
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://${address}" >/dev/null 2>&1 || true
fi
