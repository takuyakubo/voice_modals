"""Example with custom callback that saves transcriptions to file."""

import sys
import time
from pathlib import Path
from datetime import datetime

# Add src to path for running examples
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voice_modals import AudioCapture, StreamingASR


class TranscriptionLogger:
    """Logger that saves transcriptions to a file."""

    def __init__(self, output_file: str = "transcriptions.txt"):
        """
        Initialize the logger.

        Args:
            output_file: Path to output file
        """
        self.output_file = output_file
        self.transcription_count = 0

        # Create or clear the file
        with open(self.output_file, "w", encoding="utf-8") as f:
            f.write(f"Transcription Log - Started at {datetime.now()}\n")
            f.write("=" * 80 + "\n\n")

    def on_transcription(self, result):
        """
        Handle transcription result.

        Args:
            result: TranscriptionResult object
        """
        self.transcription_count += 1
        timestamp = datetime.fromtimestamp(result.timestamp).strftime("%H:%M:%S")

        # Print to console
        print(f"\n[{self.transcription_count}] [{timestamp}] [{result.language}]")
        print(f"{result.text}")
        print("-" * 80)

        # Save to file
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(f"[{self.transcription_count}] [{timestamp}] [{result.language}]\n")
            f.write(f"{result.text}\n\n")


def main():
    """Run custom callback example."""
    print("=" * 80)
    print("Custom Callback Example - Logging to File")
    print("=" * 80)

    output_file = f"transcriptions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    print(f"\nTranscriptions will be saved to: {output_file}")

    # Create logger
    logger = TranscriptionLogger(output_file)

    print("\nInitializing ASR engine...")

    # Initialize ASR engine
    asr = StreamingASR(
        model_size="base",
        device="cpu",
        language=None,  # Auto-detect language
    )

    # Initialize audio capture
    audio = AudioCapture(
        sample_rate=16000,
        chunk_duration=1.5,
    )

    # Set custom callback
    asr.set_callback(logger.on_transcription)

    print("Starting audio capture and ASR processing...")
    print("Speak into your microphone. Press Ctrl+C to stop.\n")

    try:
        audio.start()
        asr.start_processing_thread(process_interval=3.0)

        while True:
            audio_chunk = audio.get_audio_chunk(timeout=1.0)
            if audio_chunk is not None:
                asr.add_audio(audio_chunk)

    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        asr.stop_processing_thread()
        audio.stop()
        print(f"\nTotal transcriptions: {logger.transcription_count}")
        print(f"Saved to: {output_file}")
        print("Done!")


if __name__ == "__main__":
    main()
