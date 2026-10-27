#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/bidfit-uv}"
uv venv --allow-existing .venv
uv pip sync --python .venv/bin/python backend/requirements.lock
npm --prefix frontend ci --cache /tmp/bidfit-npm
npm --prefix infra ci --cache /tmp/bidfit-npm
npm --prefix frontend run build
