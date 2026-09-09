import type { AskResponse, VisualEvent, MovieState } from "../types";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function seedDemoData(): Promise<MovieState> {
  const res = await fetch(`${API_BASE}/api/seed-demo`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to load demo data" }));
    throw new Error(err.detail || "Demo seeding failed");
  }
  const data = await res.json();
  return {
    movie_id: data.movie_id,
    title: data.title,
    duration_seconds: data.duration_seconds,
    video_url: `${API_BASE}${data.video_url}`,
    events: data.events || []
  };
}

export async function uploadVideo(file: File): Promise<{ movie_id: string; file_path: string; filename: string }> {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Video upload failed");
  }
  return res.json();
}

export async function analyzeVideo(movieId: string, filePath?: string): Promise<{ movie_id: string; events: VisualEvent[] }> {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ movie_id: movieId, file_path: filePath })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Analysis failed" }));
    throw new Error(err.detail || "Video analysis failed");
  }
  return res.json();
}

export async function storeEvents(movieId: string, events: VisualEvent[], title?: string, duration?: number): Promise<any> {
  const res = await fetch(`${API_BASE}/api/store-events`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      movie_id: movieId,
      title: title || "Uploaded Video",
      duration_seconds: duration || 75.0,
      events: events
    })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Storage failed" }));
    throw new Error(err.detail || "Event storage failed");
  }
  return res.json();
}

export async function askRecall(movieId: string, question: string): Promise<AskResponse> {
  const res = await fetch(`${API_BASE}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ movie_id: movieId, question: question })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Question answering failed" }));
    throw new Error(err.detail || "Failed to answer question");
  }
  return res.json();
}

export async function checkReadiness(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/ready`);
    return res.ok;
  } catch {
    return false;
  }
}
