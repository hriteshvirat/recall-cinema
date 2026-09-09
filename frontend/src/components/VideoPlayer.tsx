import React, { useRef, forwardRef, useImperativeHandle } from "react";
import type { VisualEvent } from "../types";

interface VideoPlayerProps {
  src?: string;
  activeEvent?: VisualEvent;
  onTimeUpdate: (currentTime: number) => void;
}

export interface VideoPlayerHandle {
  seekTo: (seconds: number) => void;
  play: () => void;
  pause: () => void;
}

export const VideoPlayer = forwardRef<VideoPlayerHandle, VideoPlayerProps>(
  ({ src, activeEvent, onTimeUpdate }, ref) => {
    const videoRef = useRef<HTMLVideoElement>(null);
    const [currentTime, setCurrentTime] = React.useState(0);

    useImperativeHandle(ref, () => ({
      seekTo: (seconds: number) => {
        if (videoRef.current) {
          videoRef.current.currentTime = seconds;
          videoRef.current.play().catch(() => {});
        }
      },
      play: () => {
        videoRef.current?.play().catch(() => {});
      },
      pause: () => {
        videoRef.current?.pause();
      }
    }));

    const handleTimeUpdate = () => {
      if (videoRef.current) {
        const t = videoRef.current.currentTime;
        setCurrentTime(t);
        onTimeUpdate(t);
      }
    };

    const formatTime = (secs: number) => {
      const m = Math.floor(secs / 60);
      const s = Math.floor(secs % 60);
      return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
    };

    return (
      <div className="card" role="region" aria-label="Video Player Section">
        <div className="card-header">
          <h2 className="card-title">Media Playback</h2>
          <span className="badge">
            Current: {formatTime(currentTime)}
          </span>
        </div>

        <div className="video-wrapper">
          {src ? (
            <video
              ref={videoRef}
              src={src}
              controls
              playsInline
              className="video-element"
              onTimeUpdate={handleTimeUpdate}
              aria-label="Fictional Mystery Video Player"
            >
              Your browser does not support HTML5 video.
            </video>
          ) : (
            <div
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                justifyContent: "center",
                height: "100%",
                color: "var(--text-muted)",
                gap: "1rem"
              }}
            >
              <p style={{ fontSize: "1.1rem" }}>No video loaded yet.</p>
              <p style={{ fontSize: "0.95rem" }}>
                Click <strong>"Load Mystery Demo"</strong> or <strong>"Upload MP4"</strong> above.
              </p>
            </div>
          )}

          {src && (
            <div className="video-overlay-timestamp" aria-hidden="true">
              {formatTime(currentTime)}
            </div>
          )}
        </div>

        {activeEvent && (
          <div
            style={{
              padding: "0.75rem 1rem",
              background: "var(--bg-elevated)",
              borderRadius: "0.5rem",
              border: "1px solid var(--border-subtle)"
            }}
            role="status"
            aria-label={`Active visual event at ${formatTime(activeEvent.start_seconds)}: ${activeEvent.action}`}
          >
            <span style={{ color: "var(--accent-cyan)", fontWeight: 700, fontSize: "0.85rem" }}>
              ACTIVE EVENT [{formatTime(activeEvent.start_seconds)} - {formatTime(activeEvent.end_seconds)}]
            </span>
            <p style={{ color: "var(--text-primary)", fontWeight: 600, marginTop: "0.2rem" }}>
              {activeEvent.action}
            </p>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem", marginTop: "0.1rem" }}>
              {activeEvent.visual_description}
            </p>
          </div>
        )}
      </div>
    );
  }
);

VideoPlayer.displayName = "VideoPlayer";
