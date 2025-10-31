"""Test the streaming ASR system with a short recording."""

import time
from src.voice_modals import AudioCapture, StreamingASR

def test_system():
    """Test the system with a short recording."""
    print("=" * 80)
    print("System Test")
    print("=" * 80)
    print("\nThis will test the system for 10 seconds.")
    print("Please speak into your microphone during this time.")
    print("\nInitializing...")

    # Initialize ASR engine (using tiny model for quick testing)
    asr = StreamingASR(
        model_size="tiny",  # Smallest/fastest model for testing
        device="cpu",
        language=None,  # Auto-detect
    )

    # Initialize audio capture
    audio = AudioCapture(
        sample_rate=16000,
        chunk_duration=1.0,
    )

    # Results counter
    results_received = [0]

    # Define callback
    def on_transcription(result):
        results_received[0] += 1
        print(f"\n[Result {results_received[0]}] [{result.language}] {result.text}")
        print("-" * 80)

    asr.set_callback(on_transcription)

    print("\nStarting 10-second test...")
    print("Speak now!\n")

    try:
        # Start components
        audio.start()
        asr.start_processing_thread(process_interval=3.0)

        # Run for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            audio_chunk = audio.get_audio_chunk(timeout=1.0)
            if audio_chunk is not None:
                asr.add_audio(audio_chunk)

        # Process any remaining audio
        print("\nProcessing final audio...")
        time.sleep(3)

    finally:
        # Cleanup
        asr.stop_processing_thread()
        audio.stop()

    print("\n" + "=" * 80)
    print("Test Complete!")
    print(f"Total transcriptions received: {results_received[0]}")
    print("=" * 80)

    if results_received[0] > 0:
        print("\n✓ System is working correctly!")
    else:
        print("\n⚠ No transcriptions received. Try speaking louder or closer to the mic.")

if __name__ == "__main__":
    test_system()
