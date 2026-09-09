#!/usr/bin/env bash
set -e

# ==============================================================================
# RECALL: Start Official ClickHouse MCP Server (mcp-clickhouse)
# ==============================================================================
# This script launches the official ClickHouse MCP server exposing:
# - run_query
# - list_databases
# - list_tables
# in read-only mode over stdio (or HTTP transport) for the Google ADK Agent.
# ==============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Load environment variables if .env exists
if [ -f "$ROOT_DIR/.env" ]; then
    echo "Loading environment from $ROOT_DIR/.env..."
    export $(grep -v '^#' "$ROOT_DIR/.env" | xargs)
fi

# Set defaults for ClickHouse Cloud if not provided
export CLICKHOUSE_HOST="${CLICKHOUSE_HOST:-localhost}"
export CLICKHOUSE_PORT="${CLICKHOUSE_PORT:-8443}"
export CLICKHOUSE_USER="${CLICKHOUSE_USER:-default}"
export CLICKHOUSE_PASSWORD="${CLICKHOUSE_PASSWORD:-}"
export CLICKHOUSE_DATABASE="${CLICKHOUSE_DATABASE:-recall}"
export CLICKHOUSE_SECURE="${CLICKHOUSE_SECURE:-true}"

echo "--------------------------------------------------"
echo "Launching ClickHouse MCP Server (mcp-clickhouse)..."
echo "Host:     $CLICKHOUSE_HOST:$CLICKHOUSE_PORT"
echo "User:     $CLICKHOUSE_USER"
echo "Database: $CLICKHOUSE_DATABASE"
echo "Secure:   $CLICKHOUSE_SECURE"
echo "Mode:     Read-Only (Default)"
echo "--------------------------------------------------"

# Check if python virtual environment exists
if [ -f "$ROOT_DIR/venv/bin/mcp-clickhouse" ]; then
    exec "$ROOT_DIR/venv/bin/mcp-clickhouse" "$@"
elif [ -f "$ROOT_DIR/venv/bin/python" ]; then
    exec "$ROOT_DIR/venv/bin/python" -m mcp_clickhouse "$@"
elif which uv >/dev/null 2>&1; then
    exec uv run mcp-clickhouse "$@"
else
    exec mcp-clickhouse "$@"
fi
