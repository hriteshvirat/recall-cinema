# RECALL Architecture

> **Persistent Visual Memory for Media**  
> Built for the *Agentic Cinema* Hackathon.

RECALL enables blind and visually impaired individuals to interrogate video media across time. Instead of merely describing whatever pixels are currently in front of a camera, RECALL constructs a persistent, structured temporal memory in **ClickHouse Cloud**, queryable on-demand via a **Google ADK Agent** connected through the official **ClickHouse MCP Server (`mcp-clickhouse`)**.

---

## 1. System Architecture

```mermaid
graph TD
    subgraph Client Layer
        User["Blind / Visually Impaired User"]
        UI["RECALL Web App (React + Vite + TypeScript)"]
    end

    subgraph Backend Services
        FastAPI["FastAPI Backend (Python 3.11)"]
        GeminiVision["Gemini Video Understanding API"]
        TTS["Google Cloud Text-to-Speech"]
    end

    subgraph Agentic Reasoning Layer
        ADK["Google ADK Visual Memory Agent"]
        MCPClient["MCP Protocol Client (stdio/HTTP)"]
        OfficialMCP["Official ClickHouse MCP (mcp-clickhouse)"]
    end

    subgraph Storage Layer
        CH["ClickHouse Cloud (visual_events & movies)"]
    end

    User -->|"Uploads video or asks questions"| UI
    UI -->|"POST /api/upload & /api/analyze"| FastAPI
    FastAPI -->|"Uploads video & requests strict JSON extraction"| GeminiVision
    GeminiVision -->|"Timestamped Visual Events"| FastAPI
    FastAPI -->|"Stores into MergeTree"| CH

    UI -->|"POST /api/ask (Question)"| FastAPI
    FastAPI -->|"Dispatches query"| ADK
    ADK -->|"Formulates focused SQL & calls run_query"| MCPClient
    MCPClient -->|"Tool Execution across MCP protocol"| OfficialMCP
    OfficialMCP -->|"SQL over HTTPS (Port 8443)"| CH
    CH -->|"Temporal event rows"| OfficialMCP
    OfficialMCP -->|"MCP tool response + telemetry"| MCPClient
    MCPClient -->|"Retrieved evidence rows"| ADK
    ADK -->|"Synthesizes answer with timestamp citations"| FastAPI
    FastAPI -->|"POST /api/tts (Synthesize speech)"| TTS
    TTS -->|"Natural voice audio stream"| FastAPI
    FastAPI -->|"Answer + Timestamps + Audio + Real Trace"| UI
    UI -->|"Spoken answer playback & seekable chips"| User
```

---

## 2. Core Components

### 2.1 Video Understanding (Google Gemini)
- Uploads video using the Google GenAI File API.
- Extracts visual facts as strict, validated Pydantic JSON:
  - `start_seconds`, `end_seconds`
  - `characters` (Array of Strings)
  - `objects` (Array of Strings)
  - `location`, `action`, `visual_description`, `confidence`
- Strict prompt constraints prevent hallucinations and prioritize physical state changes, object placements, and entrances/exits.

### 2.2 Temporal Memory Store (ClickHouse Cloud)
- Events are persisted into a dedicated `visual_events` table using ClickHouse's high-performance `MergeTree` engine ordered by `(movie_id, start_seconds, event_id)`.
- Array support (`Array(String)`) enables lightning-fast `has(objects, 'brown envelope')` and `has(characters, 'Daniel')` queries.

### 2.3 Agentic Tool Layer (Official ClickHouse MCP Server)
- The agent does **not** use custom direct database queries. Instead, it utilizes the official **`mcp-clickhouse`** server.
- Supported MCP tools:
  - `run_query`: Read-only execution of ClickHouse SQL.
  - `list_tables`: Schema inspection.
  - `list_databases`: Database catalog listing.
- Telemetry (exact SQL query, execution latency in milliseconds, row count) is captured from the real MCP tool invocation and displayed in the developer trace drawer.

### 2.4 Spoken Accessibility & UI
- High contrast WCAG AAA interface with visible focus outlines and screen-reader announcements via `aria-live="polite"`.
- Clicking any timestamp evidence chip instantly seeks the HTML5 media player to the exact second in the movie.
- Speech playback powered by Google Cloud Text-to-Speech (`en-US-Journey-F`).
