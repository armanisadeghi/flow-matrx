#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../backend"

echo "Running Alembic migrations..."
alembic upgrade head
echo "✅  Migrations complete."
