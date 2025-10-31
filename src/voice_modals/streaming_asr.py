"""Streaming ASR engine using Faster-Whisper for real-time transcription."""

import threading
import time
from typing import Optional, Callable, List
from dataclasses import dataclass
import numpy as np
from faster_whisper import WhisperModel


@dataclass
class TranscriptionResult:
    """Result of a transcription."""

    text: str
    language: str
    timestamp: float
    is_partial: bool = False


class StreamingASR:
    """Streaming Automatic Speech Recognition using Whisper."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        language: Optional[str] = None,
        beam_size: int = 5,
        vad_filter: bool = True,
        min_silence_duration: float = 0.5,
    ):
        """
        Initialize the streaming ASR engine.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
            device: Device to run on ("cpu", "cuda", or "auto")
            compute_type: Computation type for faster-whisper ("int8", "float16", etc.)
            language: Language code (None for auto-detection)
            beam_size: Beam size for decoding
            vad_filter: Enable Voice Activity Detection filter
            min_silence_duration: Minimum silence duration to split utterances
        """
        print(f"Loading Whisper model: {model_size} on {device}...")
        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
        )
        print("Model loaded successfully")

        self.language = language
        self.beam_size = beam_size
        self.vad_filter = vad_filter
        self.min_silence_duration = min_silence_duration

        self.sample_rate = 16000  # Whisper expects 16kHz audio
        self.is_running = False
        self._buffer: List[np.ndarray] = []
        self._buffer_lock = threading.Lock()
        self._callback: Optional[Callable[[TranscriptionResult], None]] = None

    def transcribe_chunk(
        self, audio_data: np.ndarray, language: Optional[str] = None
    ) -> Optional[TranscriptionResult]:
        """
        Transcribe a single audio chunk.

        Args:
            audio_data: Audio data as numpy array (float32, 16kHz)
            language: Override language for this chunk

        Returns:
            TranscriptionResult or None if no speech detected
        """
        if len(audio_data) == 0:
            return None

        # Ensure audio is at least 0.1 seconds
        min_samples = int(0.1 * self.sample_rate)
        if len(audio_data) < min_samples:
            return None

        try:
            segments, info = self.model.transcribe(
                audio_data,
                language=language or self.language,
                beam_size=self.beam_size,
                vad_filter=self.vad_filter,
                vad_parameters={
                    "min_silence_duration_ms": int(self.min_silence_duration * 1000)
                },
            )

            # Combine all segments
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text)

            if not text_parts:
                return None

            full_text = " ".join(text_parts).strip()
            if not full_text:
                return None

            return TranscriptionResult(
                text=full_text,
                language=info.language,
                timestamp=time.time(),
                is_partial=False,
            )

        except Exception as e:
            print(f"Transcription error: {e}")
            return None

    def add_audio(self, audio_data: np.ndarray):
        """
        Add audio data to the processing buffer.

        Args:
            audio_data: Audio data as numpy array (float32, 16kHz)
        """
        with self._buffer_lock:
            self._buffer.append(audio_data)

    def process_buffer(self) -> Optional[TranscriptionResult]:
        """
        Process accumulated audio buffer and return transcription.

        Returns:
            TranscriptionResult or None
        """
        with self._buffer_lock:
            if not self._buffer:
                return None

            # Concatenate all buffered audio
            audio_data = np.concatenate(self._buffer)
            self._buffer.clear()

        return self.transcribe_chunk(audio_data)

    def set_callback(self, callback: Callable[[TranscriptionResult], None]):
        """
        Set a callback function to be called when transcription is ready.

        Args:
            callback: Function that receives TranscriptionResult
        """
        self._callback = callback

    def start_processing_thread(self, process_interval: float = 2.0):
        """
        Start a background thread to periodically process the buffer.

        Args:
            process_interval: Time in seconds between processing attempts
        """
        if self.is_running:
            return

        self.is_running = True

        def process_loop():
            while self.is_running:
                result = self.process_buffer()
                if result and self._callback:
                    self._callback(result)
                time.sleep(process_interval)

        self._thread = threading.Thread(target=process_loop, daemon=True)
        self._thread.start()
        print(f"Started processing thread (interval={process_interval}s)")

    def stop_processing_thread(self):
        """Stop the background processing thread."""
        self.is_running = False
        if hasattr(self, "_thread") and self._thread:
            self._thread.join(timeout=5.0)
        print("Stopped processing thread")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop_processing_thread()
