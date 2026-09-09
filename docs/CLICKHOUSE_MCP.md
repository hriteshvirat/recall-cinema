# ClickHouse MCP Integration Guide

RECALL integrates the official ClickHouse MCP server (**`ClickHouse/mcp-clickhouse`**) to provide read-only database query tools directly to Google ADK and Gemini.

---

## 1. Official MCP Server Architecture

The official `mcp-clickhouse` server bridges AI agents and ClickHouse via the Model Context Protocol:

```
RECALL ADK Agent
      │
      ▼ (MCP Tool Call: run_query)
MCP Client Session
      │
      ▼ (Standard stdio / SSE transport)
mcp-clickhouse (Official ClickHouse Server)
      │
      ▼ (HTTP/HTTPS over Port 8443 with TLS)
ClickHouse Cloud (visual_events table)
```

---

## 2. Tools Exposed by `mcp-clickhouse`

| MCP Tool Name | Description | Safety Guarantee |
| :--- | :--- | :--- |
| `run_query` | Executes arbitrary ClickHouse SQL queries against the visual memory table. | Read-Only (enforced by default) |
| `list_tables` | Lists all tables in the active database (`visual_events`, `movies`). | Read-Only |
| `list_databases`| Lists available ClickHouse database catalogs. | Read-Only |

---

## 3. Configuration & Credentials

All credentials must be supplied via environment variables or `.env`:

```bash
# ClickHouse Cloud Connection
CLICKHOUSE_HOST=your-instance.clickhouse.cloud
CLICKHOUSE_PORT=8443
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=your-clickhouse-password
CLICKHOUSE_DATABASE=recall
CLICKHOUSE_SECURE=true
```

---

## 4. Running the MCP Server Locally

To start the official ClickHouse MCP server locally:

```bash
# Using the provided script
./scripts/start_clickhouse_mcp.sh

# Or directly with python
./venv/bin/python -m mcp_clickhouse

# Or with uv
uv run mcp-clickhouse
```

---

## 5. Temporal Query Strategy in RECALL

When answering temporal visual questions, the agent formulates schema-aware ClickHouse SQL queries:

### Earliest Appearance ("Where was the envelope first seen?")
```sql
SELECT event_id, start_seconds, end_seconds, characters, objects, location, action, visual_description, confidence
FROM recall.visual_events
WHERE movie_id = 'movie_kitchen_mystery' 
  AND has(objects, 'brown envelope')
ORDER BY start_seconds ASC
LIMIT 3;
```

### Event Sequence After an Exit ("What changed after Maya left?")
```sql
SELECT event_id, start_seconds, end_seconds, characters, objects, location, action, visual_description, confidence
FROM recall.visual_events
WHERE movie_id = 'movie_kitchen_mystery'
  AND start_seconds >= (
    SELECT max(start_seconds) 
    FROM recall.visual_events 
    WHERE movie_id = 'movie_kitchen_mystery' 
      AND has(characters, 'Maya') 
      AND event_type = 'character_exited'
  )
ORDER BY start_seconds ASC;
```

### Final Location ("Where did the envelope end up?")
```sql
SELECT event_id, start_seconds, end_seconds, characters, objects, location, action, visual_description, confidence
FROM recall.visual_events
WHERE movie_id = 'movie_kitchen_mystery' 
  AND has(objects, 'brown envelope')
ORDER BY start_seconds DESC
LIMIT 5;
```
