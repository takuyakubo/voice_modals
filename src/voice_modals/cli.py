"""Command-line interface for the streaming ASR system."""

import argparse
import signal
import sys
from typing import Optional
from .audio_capture import AudioCapture
from .streaming_asr import StreamingASR, TranscriptionResult


class StreamingASRApp:
    """Main application for streaming ASR."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        language: Optional[str] = None,
        chunk_duration: float = 1.0,
        process_interval: float = 2.0,
    ):
        """
        Initialize the streaming ASR application.

        Args:
            model_size: Whisper model size
            device: Device to run on
            language: Language code (None for auto-detection)
            chunk_duration: Audio chunk duration in seconds
            process_interval: Processing interval in seconds
        """
        self.model_size = model_size
        self.device = device
        self.language = language
        self.chunk_duration = chunk_duration
        self.process_interval = process_interval

        self.audio_capture: Optional[AudioCapture] = None
        self.asr_engine: Optional[StreamingASR] = None
        self.running = False

    def on_transcription(self, result: TranscriptionResult):
        """
        Callback for when transcription is available.

        Args:
            result: Transcription result
        """
        print(f"\n[{result.language}] {result.text}")
        sys.stdout.flush()

    def run(self):
        """Run the streaming ASR application."""
        print("=" * 80)
        print("Streaming ASR System - OpenAI Whisper")
        print("=" * 80)
        print(f"Model: {self.model_size}")
        print(f"Device: {self.device}")
        print(f"Language: {self.language or 'auto-detect'}")
        print(f"Chunk duration: {self.chunk_duration}s")
        print(f"Process interval: {self.process_interval}s")
        print("=" * 80)
        print("\nPress Ctrl+C to stop\n")

        # Initialize components
        self.asr_engine = StreamingASR(
            model_size=self.model_size,
            device=self.device,
            language=self.language,
        )
        self.asr_engine.set_callback(self.on_transcription)

        self.audio_capture = AudioCapture(
            sample_rate=16000,
            chunk_duration=self.chunk_duration,
        )

        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)

        try:
            self.running = True

            # Start audio capture
            self.audio_capture.start()

            # Start ASR processing thread
            self.asr_engine.start_processing_thread(process_interval=self.process_interval)

            print("Listening... (speak into your microphone)\n")

            # Main loop: feed audio to ASR engine
            while self.running:
                audio_chunk = self.audio_capture.get_audio_chunk(timeout=1.0)
                if audio_chunk is not None:
                    self.asr_engine.add_audio(audio_chunk)

        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            self.cleanup()

    def _signal_handler(self, signum, frame):
        """Handle interrupt signal."""
        print("\n\nReceived interrupt signal. Stopping...")
        self.running = False

    def cleanup(self):
        """Clean up resources."""
        if self.asr_engine:
            self.asr_engine.stop_processing_thread()

        if self.audio_capture:
            self.audio_capture.stop()

        print("Cleanup complete. Goodbye!")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Streaming ASR system using OpenAI Whisper",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default settings (base model, CPU)
  uv run python -m voice_modals.cli

  # Use small model with Japanese
  uv run python -m voice_modals.cli --model small --language ja

  # Use GPU acceleration
  uv run python -m voice_modals.cli --model medium --device cuda

  # Adjust processing parameters
  uv run python -m voice_modals.cli --chunk-duration 2.0 --process-interval 3.0
        """,
    )

    parser.add_argument(
        "--model",
        type=str,
        default="base",
        choices=["tiny", "base", "small", "medium", "large"],
        help="Whisper model size (default: base)",
    )

    parser.add_argument(
        "--device",
        type=str,
        default="cpu",
        choices=["cpu", "cuda", "auto"],
        help="Device to run on (default: cpu)",
    )

    parser.add_argument(
        "--language",
        type=str,
        default=None,
        help="Language code (e.g., en, ja, zh). Leave empty for auto-detection.",
    )

    parser.add_argument(
        "--chunk-duration",
        type=float,
        default=1.0,
        help="Audio chunk duration in seconds (default: 1.0)",
    )

    parser.add_argument(
        "--process-interval",
        type=float,
        default=2.0,
        help="Processing interval in seconds (default: 2.0)",
    )

    args = parser.parse_args()

    # Create and run application
    app = StreamingASRApp(
        model_size=args.model,
        device=args.device,
        language=args.language,
        chunk_duration=args.chunk_duration,
        process_interval=args.process_interval,
    )

    app.run()


if __name__ == "__main__":
    main()
