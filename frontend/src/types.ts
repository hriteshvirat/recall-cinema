export interface VisualEvent {
  event_id: string;
  movie_id: string;
  start_seconds: number;
  end_seconds: number;
  event_type: string;
  characters: string[];
  objects: string[];
  location: string;
  action: string;
  visual_description: string;
  confidence: number;
}

export interface SupportingEvent {
  event_id: string;
  start_seconds: number;
  end_seconds: number;
  description: string;
}

export interface TraceStep {
  stage: string;
  detail: string;
  mcp_tool?: string;
  sql_query?: string;
  rows_returned?: number;
  duration_ms?: number;
}

export interface AskResponse {
  answer: string;
  confidence: number;
  supporting_events: SupportingEvent[];
  trace: TraceStep[];
  audio_base64?: string;
}

export interface MovieState {
  movie_id: string;
  title: string;
  duration_seconds: number;
  video_url: string;
  events: VisualEvent[];
}
