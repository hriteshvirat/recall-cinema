import os
import time
import json
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.models import (
    VisualEvent, MovieMetadata, ExtractionResult,
    AskRequest, AskResponse, UploadResponse,
    AnalyzeRequest, StoreEventsRequest, TTSRequest, TTSResponse
)
from backend.app.database import db
from backend.app.video_analyzer import video_analyzer
from backend.app.tts_service import tts_service
from backend.app.logger import logger, log_operation, log_block
from agent.recall_agent import recall_agent

app = FastAPI(
    title="RECALL API",
    description="Persistent Visual Memory Agent for Media (Agentic Cinema Hackathon)",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve media files (uploaded and sample videos)
media_dir = settings.BASE_DIR / "sample_data"
media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(settings.BASE_DIR)), name="media")

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing RECALL API...")
    try:
        db.init_db()
        logger.info("ClickHouse schema verified on startup.")
    except Exception as e:
        logger.warning(f"Could not connect to ClickHouse on startup: {e}. Note: verify credentials in .env.")

@app.get("/health")
def health_check():
    """Liveness probe."""
    return {
        "status": "healthy",
        "service": "RECALL",
        "timestamp": time.time()
    }

@app.get("/ready")
def readiness_check():
    """Readiness probe checking database connectivity."""
    try:
        ch_status = db.check_health()
        return {
            "status": "ready",
            "clickhouse": ch_status,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "error": str(e)}
        )

@app.post("/api/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """
    Accepts an MP4 video upload and stores it locally.
    """
    req_id = str(uuid.uuid4())[:8]
    movie_id = f"movie_{int(time.time())}_{req_id}"
    
    if not file.filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
        raise HTTPException(status_code=400, detail="Only video files (MP4, MOV, WEBM) are supported.")
    
    file_path = settings.UPLOAD_DIR / f"{movie_id}_{file.filename}"
    
    with log_block("video_upload", movie_id=movie_id, request_id=req_id):
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
            
    logger.info(f"Saved uploaded video to {file_path} ({len(content)} bytes)")
    return UploadResponse(
        movie_id=movie_id,
        filename=file.filename,
        file_path=str(file_path),
        duration_seconds=None,
        message="Video uploaded successfully"
    )

@app.post("/api/analyze", response_model=ExtractionResult)
def analyze_video(request: AnalyzeRequest):
    """
    Sends uploaded video to Google Gemini to extract timestamped visual events into strict JSON.
    """
    req_id = str(uuid.uuid4())[:8]
    with log_block("analyze_video", movie_id=request.movie_id, request_id=req_id):
        file_path = request.file_path
        if not file_path or not Path(file_path).exists():
            # Check demo file fallback
            if settings.SAMPLE_VIDEO_FILE.exists():
                file_path = str(settings.SAMPLE_VIDEO_FILE)
            else:
                raise HTTPException(status_code=404, detail="Video file not found for analysis.")
        
        try:
            extraction = video_analyzer.analyze_video(file_path, request.movie_id)
            return extraction
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise HTTPException(status_code=500, detail=f"Gemini video analysis failed: {str(e)}")

@app.post("/api/store-events")
def store_events(request: StoreEventsRequest):
    """
    Stores structured visual events into ClickHouse MergeTree tables.
    """
    req_id = str(uuid.uuid4())[:8]
    with log_block("store_events", movie_id=request.movie_id, request_id=req_id):
        try:
            # Ensure schema
            db.init_db()
            
            # Store movie metadata
            movie = MovieMetadata(
                movie_id=request.movie_id,
                title=request.title or "Untitled Movie",
                duration_seconds=request.duration_seconds or 75.0
            )
            db.store_movie(movie)
            
            # Batch store events
            count = db.store_visual_events(request.movie_id, request.events)
            
            return {
                "success": True,
                "movie_id": request.movie_id,
                "events_stored": count,
                "message": f"Successfully stored {count} visual events in ClickHouse"
            }
        except Exception as e:
            logger.error(f"Failed storing events in ClickHouse: {e}")
            raise HTTPException(status_code=500, detail=f"ClickHouse storage error: {str(e)}")

@app.get("/api/events/{movie_id}")
def get_movie_events(movie_id: str):
    """
    Retrieves all stored events for a movie from ClickHouse.
    """
    try:
        events = db.get_all_events(movie_id)
        return {
            "movie_id": movie_id,
            "total_events": len(events),
            "events": events
        }
    except Exception as e:
        logger.error(f"Error fetching events for {movie_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ask", response_model=AskResponse)
def ask_recall(request: AskRequest):
    """
    Agentic question flow:
    Gemini ADK Agent -> ClickHouse MCP (run_query) -> ClickHouse -> Evidence Reasoning -> TTS Spoken Output
    """
    req_id = str(uuid.uuid4())[:8]
    with log_block("agent_ask", movie_id=request.movie_id, request_id=req_id):
        try:
            # 1. Ask RECALL agent (invokes ClickHouse MCP)
            response = recall_agent.answer_question(request.movie_id, request.question)
            
            # 2. Synthesize Google TTS audio
            audio_b64, fmt = tts_service.synthesize_speech(response.answer)
            response.audio_base64 = audio_b64
            
            return response
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts", response_model=TTSResponse)
def synthesize_tts(request: TTSRequest):
    """
    Google Cloud Text-to-Speech endpoint.
    """
    audio_b64, fmt = tts_service.synthesize_speech(request.text, request.voice)
    if not audio_b64:
        raise HTTPException(status_code=500, detail="TTS synthesis failed or credentials unavailable.")
    return TTSResponse(audio_base64=audio_b64, format=fmt)

@app.post("/api/seed-demo")
def seed_demo_data():
    """
    Demo Mode: Seeds ClickHouse with the 20-event kitchen mystery benchmark dataset.
    """
    req_id = str(uuid.uuid4())[:8]
    with log_block("seed_demo_data", request_id=req_id):
        sample_path = settings.SAMPLE_DATA_FILE
        if not sample_path.exists():
            raise HTTPException(status_code=404, detail="Sample data file not found.")
        
        with open(sample_path, "r") as f:
            data = json.load(f)
            
        movie_id = data.get("movie_id", "movie_kitchen_mystery")
        title = data.get("title", "The Kitchen Hand-off (A Visual Memory Test)")
        duration = data.get("duration_seconds", 75.0)
        events_raw = data.get("events", [])
        
        events = [VisualEvent(**ev) for ev in events_raw]
        
        # Ingest into ClickHouse
        db.init_db()
        movie = MovieMetadata(movie_id=movie_id, title=title, duration_seconds=duration)
        db.store_movie(movie)
        count = db.store_visual_events(movie_id, events)
        
        video_url = "/media/sample_data/kitchen_mystery_demo.mp4"
        
        return {
            "success": True,
            "movie_id": movie_id,
            "title": title,
            "duration_seconds": duration,
            "events_stored": count,
            "video_url": video_url,
            "events": [ev.dict() for ev in events],
            "message": f"Demo benchmark loaded: {count} events stored in ClickHouse"
        }
