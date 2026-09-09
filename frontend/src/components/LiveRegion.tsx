import React from "react";
import { Activity } from "lucide-react";

interface LiveRegionProps {
  status: string;
}

export const LiveRegion: React.FC<LiveRegionProps> = ({ status }) => {
  if (!status) return null;

  return (
    <div
      className="aria-status-banner"
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      <Activity size={18} color="#10B981" aria-hidden="true" />
      <span>Status: {status}</span>
    </div>
  );
};
