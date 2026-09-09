import base64
import os
from typing import Optional, Tuple
from backend.app.config import settings
from backend.app.logger import logger

class GoogleTTSService:
    """Google-only Text-to-Speech service using Google Cloud Text-to-Speech."""

    def __init__(self):
        self._client = None
        self._initialized = False

    def _get_client(self):
        if not self._initialized:
            try:
                from google.cloud import texttospeech
                # Initializes with GOOGLE_APPLICATION_CREDENTIALS or default credentials
                self._client = texttospeech.TextToSpeechClient()
                logger.info("Google Cloud Text-to-Speech client initialized successfully.")
            except Exception as e:
                logger.warning(f"Google Cloud TTS client not initialized: {e}")
                self._client = None
            self._initialized = True
        return self._client

    def synthesize_speech(self, text: str, voice_name: Optional[str] = None) -> Tuple[Optional[str], str]:
        """
        Synthesizes speech from text using Google Cloud Text-to-Speech.
        Returns (base64_encoded_audio, audio_format).
        """
        client = self._get_client()
        if client:
            try:
                from google.cloud import texttospeech
                input_text = texttospeech.SynthesisInput(text=text)
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    name=voice_name or "en-US-Journey-F",
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3,
                    speaking_rate=1.05,
                    pitch=0.0
                )
                response = client.synthesize_speech(
                    request={"input": input_text, "voice": voice, "audio_config": audio_config}
                )
                audio_b64 = base64.b64encode(response.audio_content).decode("utf-8")
                return audio_b64, "mp3"
            except Exception as e:
                logger.error(f"Google Cloud TTS synthesis error: {e}")

        # Fallback if Google Cloud service credentials are not yet set
        # Return None so frontend can announce via accessible Web Speech API or screen reader
        return None, "none"

tts_service = GoogleTTSService()
