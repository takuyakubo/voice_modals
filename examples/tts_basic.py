"""Basic TTS usage example with phoneme/viseme output."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voice_modals import PiperTTSEngine


def main():
    """Basic TTS example."""
    print("=" * 80)
    print("Basic TTS Example - Phoneme/Viseme Output")
    print("=" * 80)

    # Initialize TTS engine
    print("\nInitializing Piper TTS engine...")
    engine = PiperTTSEngine(
        language="en-us",
        use_simplified_visemes=True,  # Use simplified viseme set
    )

    # Text to synthesize
    text = "Hello, this is a test of the text to speech system."
    print(f"\nText: {text}\n")

    # Synthesize speech
    print("Synthesizing speech...")
    result = engine.synthesize_to_file(text, "output.wav", include_json=True)

    print(f"\n✓ Audio saved to: output.wav")
    print(f"✓ Phoneme data saved to: output.json")
    print(f"\nDuration: {result.duration:.2f}s")
    print(f"Sample rate: {result.sample_rate}Hz")
    print(f"Total phonemes: {len(result.phonemes)}")

    # Display phoneme timeline
    print("\nPhoneme/Viseme Timeline:")
    print("-" * 80)
    for i, event in enumerate(result.phonemes[:10]):  # Show first 10
        print(
            f"  {event.start:.2f}-{event.end:.2f}s: "
            f"Phoneme '{event.phoneme}' → Viseme '{event.viseme}'"
        )

    if len(result.phonemes) > 10:
        print(f"  ... and {len(result.phonemes) - 10} more phonemes")

    print("\n" + "=" * 80)
    print("Done! You can now use the phoneme data for lip-sync animation.")
    print("=" * 80)


if __name__ == "__main__":
    main()
