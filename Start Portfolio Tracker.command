#!/bin/bash
# ─────────────────────────────────────────────
# Portfolio Tracker — Double-click to launch Web UI
# ─────────────────────────────────────────────

DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=8091

# Stop any previous instance on this port
lsof -ti:$PORT 2>/dev/null | xargs kill 2>/dev/null
sleep 1

echo "Starting Portfolio Tracker..."
cd "$DIR"
nohup python3 pwa/server.py > /tmp/portfolio_tracker.log 2>&1 &
sleep 2
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "✓ Portfolio Tracker started on port $PORT"
else
    echo "✗ Failed to start. Check /tmp/portfolio_tracker.log"
    read -p "Press Enter to close..."
    exit 1
fi

open -a "Google Chrome" "http://localhost:$PORT"

sleep 2
osascript -e 'tell application "Terminal" to close front window' &
exit 0
