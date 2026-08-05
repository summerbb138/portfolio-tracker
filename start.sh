#!/bin/bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$PROJECT_DIR"

echo "Starting Portfolio Tracker..."
echo "Open: http://localhost:8091"
exec python3 pwa/server.py
