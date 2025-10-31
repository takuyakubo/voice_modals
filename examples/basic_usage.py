"""Basic usage example of the streaming ASR system."""

import sys
import time
from pathlib import Path

# Add src to path for running examples
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voice_modals import AudioCapture, StreamingASR


def main():
    """Run basic streaming ASR example."""
    print("=" * 80)
    print("Basic Streaming ASR Example")
    print("=" * 80)
    print("\nInitializing ASR engine...")

    # Initialize ASR engine
    asr = StreamingASR(
        model_size="base",  # Use base model for good balance
        device="cpu",  # Change to "cuda" if you have GPU
        language="ja",  # Set to None for auto-detection
    )

    # Initialize audio capture
    audio = AudioCapture(
        sample_rate=16000,
        chunk_duration=1.0,  # Capture 1 second chunks
    )

    # Define callback for transcription results
    def on_transcription(result):
        """Print transcription results."""
        print(f"\n[{result.language}] {result.text}")
        print("-" * 80)

    # Set callback
    asr.set_callback(on_transcription)

    print("Starting audio capture and ASR processing...")
    print("Speak into your microphone. Press Ctrl+C to stop.\n")

    try:
        # Start audio capture
        audio.start()

        # Start ASR processing thread (processes every 2 seconds)
        asr.start_processing_thread(process_interval=2.0)

        # Main loop: feed audio to ASR engine
        while True:
            audio_chunk = audio.get_audio_chunk(timeout=1.0)
            if audio_chunk is not None:
                asr.add_audio(audio_chunk)

    except KeyboardInterrupt:
        print("\n\nStopping...")
    finally:
        # Cleanup
        asr.stop_processing_thread()
        audio.stop()
        print("Done!")


if __name__ == "__main__":
    main()
