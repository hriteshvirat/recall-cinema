import React from "react";
import { Database, Upload, Play, Terminal, Eye } from "lucide-react";

interface HeaderProps {
  eventCount: number;
  onLoadDemo: () => void;
  onUploadClick: () => void;
  onToggleTrace: () => void;
  isTraceOpen: boolean;
  isLoading: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  eventCount,
  onLoadDemo,
  onUploadClick,
  onToggleTrace,
  isTraceOpen,
  isLoading
}) => {
  return (
    <header className="app-header" role="banner">
      <div className="brand-section">
        <div className="brand-title">
          <Eye size={36} color="#38BDF8" aria-hidden="true" />
          <span>RECALL</span>
        </div>
        <p className="brand-tagline">
          Persistent visual memory for media. <em>Ask what happened, not just what is happening.</em>
        </p>
      </div>

      <div className="header-badges">
        <div className="badge badge-clickhouse" role="status" aria-label={`ClickHouse visual memory has ${eventCount} events stored`}>
          <Database size={16} color="#FBBF24" aria-hidden="true" />
          <span>ClickHouse: {eventCount} Visual Events</span>
          <span className="badge-pulse" aria-hidden="true"></span>
        </div>

        <button
          type="button"
          className="btn btn-amber"
          onClick={onLoadDemo}
          disabled={isLoading}
          aria-label="Load fictional mystery video and 20 visual events demo dataset"
        >
          <Play size={18} aria-hidden="true" />
          <span>Load Mystery Demo</span>
        </button>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={onUploadClick}
          disabled={isLoading}
          aria-label="Upload custom MP4 video for analysis"
        >
          <Upload size={18} aria-hidden="true" />
          <span>Upload MP4</span>
        </button>

        <button
          type="button"
          className="btn btn-secondary"
          onClick={onToggleTrace}
          aria-expanded={isTraceOpen}
          aria-controls="developer-trace-drawer"
          aria-label="Toggle developer trace drawer to inspect ClickHouse MCP queries"
        >
          <Terminal size={18} aria-hidden="true" />
          <span>Trace Drawer</span>
        </button>
      </div>
    </header>
  );
};
