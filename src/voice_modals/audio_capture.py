"""Real-time audio capture module using PyAudio."""

import queue
import threading
from typing import Optional, Callable
import pyaudio
import numpy as np


class AudioCapture:
    """Captures audio from microphone in real-time and provides it as chunks."""

    def __init__(
        self,
        sample_rate: int = 16000,
        chunk_duration: float = 1.0,
        channels: int = 1,
        format: int = pyaudio.paInt16,
    ):
        """
        Initialize the audio capture.

        Args:
            sample_rate: Audio sample rate in Hz (Whisper uses 16kHz)
            chunk_duration: Duration of each audio chunk in seconds
            channels: Number of audio channels (1 for mono)
            format: PyAudio format (paInt16 for 16-bit audio)
        """
        self.sample_rate = sample_rate
        self.chunk_duration = chunk_duration
        self.channels = channels
        self.format = format
        self.chunk_size = int(sample_rate * chunk_duration)

        self.audio = pyaudio.PyAudio()
        self.stream: Optional[pyaudio.Stream] = None
        self.audio_queue: queue.Queue = queue.Queue()
        self.is_recording = False
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Start capturing audio from the microphone."""
        if self.is_recording:
            return

        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self._audio_callback,
        )

        self.is_recording = True
        self.stream.start_stream()
        print(f"Audio capture started (sample_rate={self.sample_rate}Hz)")

    def stop(self):
        """Stop capturing audio."""
        if not self.is_recording:
            return

        self.is_recording = False

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        print("Audio capture stopped")

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for PyAudio stream."""
        if status:
            print(f"Audio callback status: {status}")

        # Convert bytes to numpy array
        audio_data = np.frombuffer(in_data, dtype=np.int16)
        # Normalize to float32 [-1.0, 1.0] as expected by Whisper
        audio_data = audio_data.astype(np.float32) / 32768.0

        self.audio_queue.put(audio_data)
        return (in_data, pyaudio.paContinue)

    def get_audio_chunk(self, timeout: Optional[float] = None) -> Optional[np.ndarray]:
        """
        Get the next audio chunk from the queue.

        Args:
            timeout: Maximum time to wait for audio chunk in seconds

        Returns:
            Audio data as numpy array, or None if timeout
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def clear_queue(self):
        """Clear all pending audio chunks from the queue."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

    def __del__(self):
        """Cleanup on deletion."""
        self.stop()
        if hasattr(self, "audio"):
            self.audio.terminate()
