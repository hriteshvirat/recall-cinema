from typing import List, Optional
from pydantic import BaseModel, Field

class VisualEvent(BaseModel):
    event_id: str = Field(..., description="Unique event identifier, e.g. evt_01")
    movie_id: str = Field(..., description="Unique identifier for the movie")
    start_seconds: float = Field(..., ge=0.0, description="Start timestamp in seconds")
    end_seconds: float = Field(..., ge=0.0, description="End timestamp in seconds")
    event_type: str = Field(..., description="Type of event: character_entered, object_placed, object_moved, state_change, etc.")
    characters: List[str] = Field(default_factory=list, description="List of characters appearing in this event")
    objects: List[str] = Field(default_factory=list, description="List of prominent objects involved")
    location: str = Field(..., description="Scene location or zone, e.g. kitchen table, kitchen counter")
    action: str = Field(..., description="Concise description of the action taken")
    visual_description: str = Field(..., description="Detailed, visually supported description of what occurred")
    confidence: float = Field(default=0.95, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")

class MovieMetadata(BaseModel):
    movie_id: str = Field(..., description="Unique identifier for the movie")
    title: str = Field(..., description="Title of the video/movie")
    duration_seconds: float = Field(..., ge=0.0, description="Total duration in seconds")
    created_at: Optional[str] = Field(default=None, description="ISO timestamp")

class ExtractionResult(BaseModel):
    movie_id: str
    events: List[VisualEvent]

class SupportingEvent(BaseModel):
    event_id: str
    start_seconds: float
    end_seconds: float
    description: str

class TraceStep(BaseModel):
    stage: str
    detail: str
    mcp_tool: Optional[str] = None
    sql_query: Optional[str] = None
    rows_returned: Optional[int] = None
    duration_ms: Optional[float] = None

class AskRequest(BaseModel):
    movie_id: str
    question: str

class AskResponse(BaseModel):
    answer: str
    confidence: float
    supporting_events: List[SupportingEvent]
    trace: List[TraceStep]
    audio_base64: Optional[str] = None

class UploadResponse(BaseModel):
    movie_id: str
    filename: str
    file_path: str
    duration_seconds: Optional[float] = None
    message: str

class AnalyzeRequest(BaseModel):
    movie_id: str
    file_path: Optional[str] = None

class StoreEventsRequest(BaseModel):
    movie_id: str
    title: Optional[str] = "Untitled Video"
    duration_seconds: Optional[float] = 75.0
    events: List[VisualEvent]

class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None

class TTSResponse(BaseModel):
    audio_base64: str
    format: str = "mp3"
