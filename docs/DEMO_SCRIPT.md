# RECALL: 45-Second Hackathon Demo Video Script

> **Pacing**: Confident, clear, and snappy  
> **Target Duration**: 40–48 seconds  
> **Key Message**: *"Existing tools describe what is visible now. RECALL remembers what happened over time."*

---

## Shot-by-Shot Script

| Time | On-Screen Action (What to Record) | Voiceover (What to Say) | Key Architecture Callout |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:08** | Open [recall-cinema.vercel.app](https://recall-cinema.vercel.app). Screen shows high-contrast UI with the **"ClickHouse: 20 Visual Events"** badge and video player. | *"For blind viewers, traditional accessibility tools only describe what’s on screen right now. If an object is moved, hidden, or taken off-screen, continuity is lost."* | **Problem Statement** |
| **0:08 - 0:17** | Click **"Load Mystery Demo"**. The 75-second benchmark video *"The Kitchen Hand-off"* appears. Pan briefly over the visual event timeline below the player. | *"Meet RECALL: persistent visual memory for media. Powered by Google Gemini, it extracts structured temporal events and indexes them into ClickHouse Cloud."* | **Gemini Vision + ClickHouse** |
| **0:17 - 0:27** | Click the preset question chip: **"Where did the envelope end up?"** The question submits; the status updates to *"Searching visual memory via ClickHouse MCP..."*. | *"Instead of asking what is visible now, a blind user can ask: 'Where did the envelope end up?' Our Google ADK agent queries ClickHouse via the official ClickHouse MCP server."* | **Google ADK + ClickHouse MCP** |
| **0:27 - 0:38** | The **Answer Card** pops up. Click **"Read Answer Aloud"** to hear Google TTS speak: *"The envelope ended up hidden inside the top-right cabinet drawer..."* Then **click the `00:38` evidence chip**; the video player instantly jumps to 00:38 showing Daniel hiding the envelope. | *"RECALL answers with precise temporal reasoning and speaks aloud with Google TTS. Even better: every answer cites clickable timestamp evidence that jumps the media player directly to the moment it happened."* | **Google TTS + Interactive Seeking** |
| **0:38 - 0:45** | Click **"Trace Drawer"** on the top right. Slide-over drawer reveals the authentic `mcp-clickhouse` `run_query` telemetry, SQL statement, latency, and row count. | *"Under the hood, real ClickHouse MCP queries make this temporal memory verifiable and transparent. RECALL: Ask what happened, not just what is happening."* | **Runtime Proof & Closing** |

---

## 💡 Recording Tips for Maximum Judge Impact

1. **Audio**: Keep system audio enabled so judges hear Google Cloud TTS speaking the answer at 0:28.
2. **Cursor Movement**: Move your mouse deliberately:
   - Hover over the **ClickHouse 20 Events badge**.
   - Click the question chip **"Where did the envelope end up?"**.
   - Click the **`00:38` timestamp chip** to show instantaneous video seeking.
   - Open the **Trace Drawer** at the end to showcase genuine MCP runtime integration.
3. **Pacing**: Aim for ~130-140 words total (the voiceover script above is 132 words), leaving 2-3 seconds of natural pauses for UI reactions.
