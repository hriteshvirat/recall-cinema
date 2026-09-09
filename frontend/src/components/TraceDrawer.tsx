import React from "react";
import type { TraceStep } from "../types";
import { X, Database, Terminal, Cpu, Clock, CheckCircle2, ShieldCheck } from "lucide-react";

interface TraceDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  traces: TraceStep[];
}

export const TraceDrawer: React.FC<TraceDrawerProps> = ({ isOpen, onClose, traces }) => {
  return (
    <aside
      id="developer-trace-drawer"
      className={`trace-drawer ${isOpen ? "open" : ""}`}
      role="complementary"
      aria-label="Developer Architecture Trace Drawer"
      aria-hidden={!isOpen}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", borderBottom: "1px solid var(--border-subtle)", paddingBottom: "1rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <Terminal size={22} color="#38BDF8" aria-hidden="true" />
          <h2 style={{ fontSize: "1.2rem", fontWeight: 700, color: "#FFFFFF" }}>Developer Trace</h2>
        </div>
        <button
          type="button"
          className="btn btn-secondary"
          onClick={onClose}
          style={{ padding: "0.4rem" }}
          aria-label="Close developer trace drawer"
        >
          <X size={20} aria-hidden="true" />
        </button>
      </div>

      <div style={{ background: "rgba(16, 185, 129, 0.1)", border: "1px solid var(--accent-emerald)", borderRadius: "0.5rem", padding: "0.75rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
        <ShieldCheck size={18} color="#10B981" aria-hidden="true" />
        <span style={{ fontSize: "0.85rem", color: "#34D399", fontWeight: 600 }}>
          Authentic ClickHouse MCP Runtime Execution
        </span>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {traces.length === 0 ? (
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>
            No trace generated yet. Ask a question or load the demo dataset to view the runtime MCP tool calls and reasoning stages.
          </p>
        ) : (
          traces.map((step, idx) => {
            const isMcp = step.stage.toLowerCase().includes("mcp") || !!step.mcp_tool;
            return (
              <div key={idx} className={`trace-step ${isMcp ? "mcp-query" : ""}`}>
                <div className="trace-stage">
                  <div style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                    {isMcp ? (
                      <Database size={16} color="#F59E0B" aria-hidden="true" />
                    ) : (
                      <Cpu size={16} color="#38BDF8" aria-hidden="true" />
                    )}
                    <span>{step.stage}</span>
                  </div>
                  {step.duration_ms !== undefined && (
                    <span style={{ display: "flex", alignItems: "center", gap: "0.2rem", color: "var(--text-muted)", fontFamily: "var(--font-mono)", fontSize: "0.75rem" }}>
                      <Clock size={12} aria-hidden="true" />
                      {step.duration_ms}ms
                    </span>
                  )}
                </div>

                <p style={{ fontSize: "0.9rem", color: "var(--text-primary)" }}>
                  {step.detail}
                </p>

                {step.sql_query && (
                  <div>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.25rem", textTransform: "uppercase" }}>
                      Executed SQL via ClickHouse MCP:
                    </div>
                    <pre className="trace-sql">{step.sql_query}</pre>
                  </div>
                )}

                {step.rows_returned !== undefined && (
                  <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.8rem", color: "#FBBF24" }}>
                    <CheckCircle2 size={14} aria-hidden="true" />
                    <span>ClickHouse Rows Returned: {step.rows_returned}</span>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </aside>
  );
};
