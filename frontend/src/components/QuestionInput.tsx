import React, { useState } from "react";
import { Search, Send, Sparkles } from "lucide-react";

interface QuestionInputProps {
  onAsk: (question: string) => void;
  isLoading: boolean;
}

const PRESET_QUESTIONS = [
  "Where was the envelope first placed?",
  "Who moved the envelope?",
  "Where did it end up?",
  "Who entered after Maya left?",
  "Was the envelope still on the table later?",
  "What changed in the kitchen?"
];

export const QuestionInput: React.FC<QuestionInputProps> = ({ onAsk, isLoading }) => {
  const [question, setQuestion] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (question.trim() && !isLoading) {
      onAsk(question.trim());
    }
  };

  const handlePresetClick = (preset: string) => {
    setQuestion(preset);
    onAsk(preset);
  };

  return (
    <div className="card question-container" role="region" aria-label="Ask Question Section">
      <div className="card-header">
        <h2 className="card-title">
          <Search size={22} color="#38BDF8" aria-hidden="true" />
          <span>Ask RECALL</span>
        </h2>
        <span style={{ fontSize: "0.9rem", color: "var(--text-secondary)" }}>
          Temporal memory powered by ClickHouse & Gemini
        </span>
      </div>

      <form onSubmit={handleSubmit} className="question-box">
        <label htmlFor="recall-question-input" className="sr-only">
          Ask a question about past visual events in the media
        </label>
        <input
          id="recall-question-input"
          type="text"
          className="question-input"
          placeholder="e.g. Where did the envelope end up? Who moved it?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={isLoading}
          autoComplete="off"
        />
        <button
          type="submit"
          className="btn btn-primary"
          disabled={isLoading || !question.trim()}
          aria-label="Submit question to RECALL agent"
        >
          {isLoading ? (
            <span>Reasoning...</span>
          ) : (
            <>
              <Send size={18} aria-hidden="true" />
              <span>Ask</span>
            </>
          )}
        </button>
      </form>

      <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.85rem", color: "var(--text-muted)" }}>
          <Sparkles size={14} color="#F59E0B" aria-hidden="true" />
          <span>Suggested Temporal Questions:</span>
        </div>
        <div className="preset-queries">
          {PRESET_QUESTIONS.map((q) => (
            <button
              key={q}
              type="button"
              className="preset-chip"
              onClick={() => handlePresetClick(q)}
              disabled={isLoading}
            >
              {q}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
