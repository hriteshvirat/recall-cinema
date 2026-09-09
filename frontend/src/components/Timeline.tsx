import React from "react";
import type { VisualEvent } from "../types";
import { Clock } from "lucide-react";

interface TimelineProps {
  events: VisualEvent[];
  currentTime: number;
  onSeek: (seconds: number) => void;
}

export const Timeline: React.FC<TimelineProps> = ({ events, currentTime, onSeek }) => {
  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  if (events.length === 0) {
    return null;
  }

  return (
    <div className="card timeline-section" role="region" aria-label="Visual Event Memory Timeline">
      <div className="card-header">
        <h3 className="card-title">
          <Clock size={20} color="#38BDF8" aria-hidden="true" />
          <span>Visual Event Memory Timeline</span>
        </h3>
        <span style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
          {events.length} structured events in ClickHouse
        </span>
      </div>

      <div
        className="timeline-track"
        tabIndex={0}
        role="group"
        aria-label="Chronological event nodes. Use tab and enter to seek video to event."
      >
        {events.map((ev) => {
          const isActive = currentTime >= ev.start_seconds && currentTime < ev.end_seconds;
          return (
            <button
              key={ev.event_id}
              type="button"
              className={`timeline-node ${isActive ? "active" : ""}`}
              onClick={() => onSeek(ev.start_seconds)}
              aria-label={`Jump to event at ${formatTime(ev.start_seconds)}: ${ev.action}`}
            >
              <div className="node-time">{formatTime(ev.start_seconds)}</div>
              <div className="node-title">{ev.action}</div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", textTransform: "uppercase" }}>
                {ev.event_type.replace("_", " ")}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
