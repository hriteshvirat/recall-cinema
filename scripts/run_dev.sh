#!/usr/bin/env bash
set -e

# ==============================================================================
# RECALL: Local Development Runner
# Launches FastAPI backend on :8000 and Vite frontend on :5173 concurrently
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "=================================================="
echo "Starting RECALL Local Development Environment..."
echo "=================================================="

# Check venv
if [ ! -d "$ROOT_DIR/venv" ]; then
    echo "Creating virtualenv..."
    python3 -m venv "$ROOT_DIR/venv"
    "$ROOT_DIR/venv/bin/pip" install -r "$ROOT_DIR/backend/requirements.txt" pillow
fi

# Trap SIGINT to kill background processes on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $(jobs -p) 2>/dev/null || true
}
trap cleanup EXIT

# 1. Start FastAPI Backend
echo "Starting FastAPI Backend on http://localhost:8000..."
(
    cd "$ROOT_DIR"
    PYTHONPATH="$ROOT_DIR" "$ROOT_DIR/venv/bin/uvicorn" backend.app.main:app --host 0.0.0.0 --port 8000 --reload
) &

# 2. Start Vite Frontend
echo "Starting Vite Frontend on http://localhost:5173..."
(
    cd "$ROOT_DIR/frontend"
    npm run dev -- --host
) &

# Wait for all background jobs
wait
