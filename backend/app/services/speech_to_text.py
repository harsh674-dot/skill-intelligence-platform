import os
import logging
import wave
import struct
import json
from typing import Optional

logger = logging.getLogger(__name__)


class SpeechToTextService:
    """
    Speech-to-Text (Section 13a):
    Open-source Whisper model for video transcription.

    Uses OpenAI Whisper (open-source) self-hosted on government-empanelled
    cloud GPUs. Commercial API can be a fallback if budget allows.
    """

    def __init__(self):
        self.model_path = os.environ.get("WHISPER_MODEL", "base")
        self.model = None

    def load_model(self) -> bool:
        """Load Whisper model. Returns True if successful."""
        try:
            import whisper
            self.model = whisper.load_model(self.model_path)
            logger.info(f"Whisper model loaded: {self.model_path}")
            return True
        except ImportError:
            logger.warning("Whisper not installed. Will use fallback transcription.")
            return False
        except Exception as exc:
            logger.error(f"Failed to load Whisper model: {exc}")
            return False

    def transcribe(self, audio_path: str, language: str = "en") -> dict:
        """
        Transcribe audio/video file to text.

        Returns: {"text": "...", "language": "...", "segments": [...]}
        """
        if self.model is None:
            if not self.load_model():
                return self._fallback_transcribe(audio_path, language)

        try:
            result = self.model.transcribe(audio_path, language=language)
            return {
                "text": result["text"],
                "language": result.get("language", language),
                "segments": result.get("segments", []),
            }
        except Exception as exc:
            logger.error(f"Transcription failed: {exc}")
            return self._fallback_transcribe(audio_path, language)

    def _fallback_transcribe(self, audio_path: str, language: str = "en") -> dict:
        """Fallback transcription using file metadata and basic analysis."""
        import pathlib
        import mimetypes

        file_path = pathlib.Path(audio_path)
        file_name = file_path.name
        file_size = file_path.stat().st_size if file_path.exists() else 0

        text = self._extract_text_fallback(audio_path, file_name, file_size, language)
        duration = self._estimate_duration(audio_path, file_size)

        return {
            "text": text,
            "language": language,
            "segments": [
                {
                    "start": 0,
                    "end": duration,
                    "text": text,
                }
            ],
            "metadata": {
                "filename": file_name,
                "file_size_bytes": file_size,
                "duration_seconds": duration,
                "language": language,
                "fallback": True,
                "method": "metadata_extraction",
            },
        }

    def _extract_text_fallback(self, audio_path: str, filename: str, file_size: int, language: str) -> str:
        """Extract any text content from file or generate from filename."""
        import pathlib

        file_path = pathlib.Path(audio_path)

        if file_path.suffix.lower() in [".txt", ".srt", ".vtt", ".json"]:
            try:
                content = file_path.read_text(encoding="utf-8", errors="replace")
                if len(content.strip()) > 0:
                    return content.strip()[:10000]
            except Exception:
                pass

        if file_path.suffix.lower() in [".wav", ".mp3", ".mp4", ".webm", ".ogg", ".flac"]:
            sample_rate = self._read_wav_sample_rate(str(file_path))
            if sample_rate:
                duration = self._estimate_duration(audio_path, file_size)
                return (
                    f"[Audio file: {filename}, {file_size} bytes, "
                    f"~{duration:.1f}s duration, sample rate: {sample_rate}Hz, "
                    f"language: {language}. Transcription requires whisper model for text content.]"
                )

        base_name = file_path.stem
        words = base_name.replace("_", " ").replace("-", " ").split()
        if words:
            return f"[Transcription of {filename}: audio content requires whisper model for full transcription.]"
        return f"[Transcription of {filename}: audio content requires whisper model.]"

    def _read_wav_sample_rate(self, wav_path: str) -> Optional[int]:
        """Read sample rate from WAV file header."""
        try:
            with open(wav_path, "rb") as f:
                header = f.read(44)
                if len(header) >= 24 and header[0:4] == b"RIFF" and header[8:12] == b"WAVE":
                    sample_rate = struct.unpack("<I", header[24:28])[0]
                    return sample_rate
        except Exception:
            pass
        return None

    def _estimate_duration(self, audio_path: str, file_size: int) -> float:
        """Estimate audio duration from file properties."""
        try:
            import wave
            with wave.open(audio_path, "rb") as wf:
                frames = wf.getnframes()
                rate = wf.getframerate()
                if rate and frames:
                    return frames / float(rate)
        except Exception:
            pass
        if file_size > 0:
            return max(1.0, file_size / 1000.0)
        return 1.0

    def transcribe_with_fallback(self, audio_path: str, language: str = "en") -> str:
        """Transcribe with graceful degradation."""
        result = self.transcribe(audio_path, language)
        return result.get("text", "")
