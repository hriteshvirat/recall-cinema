import os
import time
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from backend.app.config import settings
from backend.app.models import VisualEvent, ExtractionResult
from backend.app.logger import logger, log_operation

class GeminiVideoAnalyzer:
    def __init__(self):
        self._client = None
        self._discovered_model: Optional[str] = None

    def _get_client(self):
        if self._client is None:
            from google import genai
            api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY not configured. Analysis will require active key or return mock.")
                return None
            self._client = genai.Client(api_key=api_key)
        return self._client

    def get_best_model(self) -> str:
        """
        Dynamically query available Gemini models and select the best supported model for video understanding.
        """
        if self._discovered_model:
            return self._discovered_model

        client = self._get_client()
        preferred_order = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro"
        ]

        if client:
            try:
                # Query available models from the Gemini API
                models = client.models.list()
                available_names = [m.name.replace("models/", "") for m in models]
                logger.info(f"Discovered {len(available_names)} Gemini models in API.")
                for preferred in preferred_order:
                    if preferred in available_names:
                        self._discovered_model = preferred
                        logger.info(f"Dynamically selected Gemini video model: {self._discovered_model}")
                        return self._discovered_model
                # If specific preferred names aren't found, find any flash model
                for name in available_names:
                    if "flash" in name and "gemini" in name:
                        self._discovered_model = name
                        logger.info(f"Selected fallback Gemini flash model: {self._discovered_model}")
                        return self._discovered_model
            except Exception as e:
                logger.warning(f"Could not dynamically list Gemini models: {e}. Using configured default.")

        # Fallback to configured setting
        self._discovered_model = settings.GEMINI_VISION_MODEL or "gemini-2.0-flash"
        return self._discovered_model

    def analyze_video(self, video_path: str, movie_id: str) -> ExtractionResult:
        """
        Analyzes a video file with Gemini and extracts timestamped visual events into strict JSON.
        """
        start_time = time.time()
        client = self._get_client()
        if not client:
            raise ValueError("Google Gemini API client is not initialized. Please configure GEMINI_API_KEY.")

        model_name = self.get_best_model()
        logger.info(f"Uploading video {video_path} to Gemini File API for analysis using model {model_name}...")

        # 1. Upload video file to Gemini File API
        file_ref = client.files.upload(file=video_path)
        logger.info(f"Uploaded video to Gemini. File name: {file_ref.name}. Checking processing state...")

        # 2. Wait for processing if needed
        while file_ref.state.name == "PROCESSING":
            time.sleep(2)
            file_ref = client.files.get(name=file_ref.name)
            logger.info(f"Video processing state: {file_ref.state.name}")

        if file_ref.state.name == "FAILED":
            raise RuntimeError(f"Gemini video processing failed: {file_ref.error}")

        # 3. Formulate extraction prompt
        system_instruction = (
            "You are a computer vision expert analyzing video media for blind and visually impaired users. "
            "Your job is to extract an objective, timestamped log of all visual events in the video. "
            "RULES:\n"
            "1. Only describe visually supported facts. Do not invent or assume motivations.\n"
            "2. Preserve exact timestamps in seconds (start_seconds and end_seconds).\n"
            "3. Separate distinct events clearly.\n"
            "4. Prioritize persistent state changes, object placement, object movement, character entrances and exits, "
            "important actions, and scene transitions.\n"
            "5. For each event, identify all visible characters, objects, location, concise action, and visual description.\n"
            "6. Output must strictly conform to the specified JSON schema."
        )

        prompt = (
            f"Extract all visual events from this video for movie_id '{movie_id}'.\n"
            "Return a JSON object with keys:\n"
            "- 'movie_id': string\n"
            "- 'events': array of objects, where each object has:\n"
            "  - 'event_id': string (e.g. 'evt_01', 'evt_02')\n"
            "  - 'movie_id': string\n"
            "  - 'start_seconds': number (float in seconds)\n"
            "  - 'end_seconds': number (float in seconds)\n"
            "  - 'event_type': string ('character_entered', 'object_placed', 'object_moved', 'state_change', 'character_exited', etc.)\n"
            "  - 'characters': array of strings\n"
            "  - 'objects': array of strings\n"
            "  - 'location': string\n"
            "  - 'action': string\n"
            "  - 'visual_description': string\n"
            "  - 'confidence': number between 0.0 and 1.0"
        )

        from google.genai import types
        response = client.models.generate_content(
            model=model_name,
            contents=[file_ref, prompt],
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                temperature=0.1
            )
        )

        raw_text = response.text
        logger.info(f"Received Gemini response ({len(raw_text)} chars). Parsing JSON...")

        data = json.loads(raw_text)
        result = ExtractionResult(**data)
        
        elapsed = (time.time() - start_time) * 1000
        log_operation(
            "gemini_video_analysis",
            movie_id=movie_id,
            duration_ms=elapsed,
            success=True,
            extra={"model": model_name, "event_count": len(result.events)}
        )
        return result

video_analyzer = GeminiVideoAnalyzer()
