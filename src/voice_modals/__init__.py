"""Voice Modals - Local Streaming ASR System using OpenAI Whisper."""

__version__ = "0.1.0"

from .audio_capture import AudioCapture
from .streaming_asr import StreamingASR

__all__ = ["AudioCapture", "StreamingASR"]
