import React, { useState, useEffect, useRef } from "react";
import type { AskResponse } from "../types";
import { Volume2, VolumeX, PlayCircle, ShieldCheck, Clock } from "lucide-react";

interface AnswerCardProps {
  response: AskResponse | null;
  onSeek: (seconds: number) => void;
}

export const AnswerCard: React.FC<AnswerCardProps> = ({ response, onSeek }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [autoSpeak, setAutoSpeak] = useState(() => {
    return localStorage.getItem("recall_auto_speak") === "true";
  });
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Auto-play TTS audio when new response arrives if autoSpeak is enabled
  useEffect(() => {
    if (response && autoSpeak) {
      speakAnswer();
    }
  }, [response]);

  const speakAnswer = () => {
    if (!response) return;

    // Stop current audio if playing
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
    }

    // 1. Prefer Google TTS Audio if audio_base64 is available
    if (response.audio_base64) {
      try {
        const audio = new Audio(`data:audio/mp3;base64,${response.audio_base64}`);
        audioRef.current = audio;
        setIsPlaying(true);
        audio.onended = () => setIsPlaying(false);
        audio.onerror = () => {
          setIsPlaying(false);
          browserSpeakFallback(response.answer);
        };
        audio.play().catch(() => {
          browserSpeakFallback(response.answer);
        });
        return;
      } catch (err) {
        console.warn("Audio element play error:", err);
      }
    }

    // 2. Standard Web Speech API fallback
    browserSpeakFallback(response.answer);
  };

  const browserSpeakFallback = (text: string) => {
    if ("speechSynthesis" in window) {
      setIsPlaying(true);
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.0;
      utterance.onend = () => setIsPlaying(false);
      utterance.onerror = () => setIsPlaying(false);
      window.speechSynthesis.speak(utterance);
    }
  };

  const stopSpeaking = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    setIsPlaying(false);
  };

  const handleAutoSpeakChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setAutoSpeak(e.target.checked);
    localStorage.setItem("recall_auto_speak", e.target.checked ? "true" : "false");
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  if (!response) {
    return null;
  }

  return (
    <div className="answer-card" role="region" aria-label="Visual Memory Answer">
      <div className="answer-header">
        <span style={{ fontSize: "0.9rem", fontWeight: 700, color: "var(--accent-cyan)", textTransform: "uppercase" }}>
          RECALL Synthesis
        </span>
        <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", color: "#34D399", fontSize: "0.85rem", fontWeight: 600 }}>
          <ShieldCheck size={16} aria-hidden="true" />
          <span>Confidence: {Math.round(response.confidence * 100)}%</span>
        </div>
      </div>

      <p className="answer-text" role="document">
        {response.answer}
      </p>

      {response.supporting_events && response.supporting_events.length > 0 && (
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "0.4rem" }}>
            <Clock size={14} color="#F59E0B" aria-hidden="true" />
            <span>ClickHouse Supporting Timestamps (Click to Seek Media):</span>
          </div>
          <div className="evidence-chips">
            {response.supporting_events.map((ev, idx) => (
              <button
                key={idx}
                type="button"
                className="evidence-chip"
                onClick={() => onSeek(ev.start_seconds)}
                aria-label={`Seek video to timestamp ${formatTime(ev.start_seconds)}: ${ev.description}`}
              >
                <PlayCircle size={16} aria-hidden="true" />
                <span>{formatTime(ev.start_seconds)}</span>
                <span style={{ fontWeight: 400, opacity: 0.9 }}>• {ev.description}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="spoken-controls">
        <button
          type="button"
          className="btn btn-primary"
          onClick={isPlaying ? stopSpeaking : speakAnswer}
          aria-label={isPlaying ? "Stop speech playback" : "Read answer aloud"}
        >
          {isPlaying ? (
            <>
              <VolumeX size={18} aria-hidden="true" />
              <span>Stop Speaking</span>
            </>
          ) : (
            <>
              <Volume2 size={18} aria-hidden="true" />
              <span>Read Answer Aloud</span>
            </>
          )}
        </button>

        <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.9rem", cursor: "pointer", color: "var(--text-secondary)" }}>
          <input
            type="checkbox"
            checked={autoSpeak}
            onChange={handleAutoSpeakChange}
            aria-label="Automatically read answers aloud for screen-reader/blind navigation"
          />
          <span>Auto-read answers aloud</span>
        </label>
      </div>
    </div>
  );
};
