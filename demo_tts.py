"""Demo script for Piper TTS with phoneme/viseme output."""

import argparse
import json
import sys
from pathlib import Path

# Add src to path for running demo
sys.path.insert(0, str(Path(__file__).parent / "src"))

from voice_modals import PiperTTSEngine, VisemeMapper


def print_phoneme_timeline(result):
    """Print phoneme/viseme timeline in a readable format."""
    print("\n" + "=" * 80)
    print("Phoneme/Viseme Timeline")
    print("=" * 80)
    print(f"Text: {result.text}")
    print(f"Duration: {result.duration:.2f}s")
    print(f"Sample Rate: {result.sample_rate}Hz")
    print("-" * 80)
    print(f"{'Time':>12} {'Phoneme':>10} {'Viseme':>10} {'Description'}")
    print("-" * 80)

    for event in result.phonemes:
        time_str = f"{event.start:.2f}-{event.end:.2f}s"
        desc = VisemeMapper.get_viseme_description(event.viseme)
        print(f"{time_str:>12} {event.phoneme:>10} {event.viseme:>10} {desc}")

    print("=" * 80)


def visualize_timeline(result, width=80):
    """Create a simple ASCII visualization of the timeline."""
    print("\n" + "=" * width)
    print("Timeline Visualization")
    print("=" * width)

    # Group consecutive same visemes
    groups = []
    current_viseme = None
    current_start = 0

    for event in result.phonemes:
        if event.viseme != current_viseme:
            if current_viseme is not None:
                groups.append((current_viseme, current_start, event.start))
            current_viseme = event.viseme
            current_start = event.start

    # Add final group
    if current_viseme is not None:
        groups.append((current_viseme, current_start, result.duration))

    # Create timeline
    timeline = [" "] * width
    labels = []

    for viseme, start, end in groups:
        start_pos = int((start / result.duration) * width)
        end_pos = int((end / result.duration) * width)

        # Fill with viseme character
        for i in range(start_pos, min(end_pos, width)):
            timeline[i] = viseme[0] if viseme else " "

        # Store label
        labels.append(f"{viseme}({start:.1f}s)")

    print("".join(timeline))
    print("-" * width)
    print("Visemes: " + ", ".join(labels))
    print("=" * width)


def main():
    """Run TTS demo."""
    parser = argparse.ArgumentParser(
        description="Piper TTS Demo with Phoneme/Viseme Output",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  uv run python demo_tts.py "Hello, world!"

  # Save to file
  uv run python demo_tts.py "Hello, world!" -o output.wav

  # Japanese text
  uv run python demo_tts.py "こんにちは、世界" --language ja

  # Use simplified visemes
  uv run python demo_tts.py "Hello" --simplified

  # Show available voices
  uv run python demo_tts.py --list-voices
        """,
    )

    parser.add_argument("text", nargs="?", help="Text to synthesize")

    parser.add_argument(
        "-o", "--output", type=str, help="Output WAV file path (optional)"
    )

    parser.add_argument(
        "--model", type=str, help="Path to Piper model file (.onnx)"
    )

    parser.add_argument(
        "--language",
        type=str,
        default="en-us",
        help="Language code (default: en-us)",
    )

    parser.add_argument(
        "--speaker", type=str, help="Speaker name/ID for multi-speaker models"
    )

    parser.add_argument(
        "--simplified",
        action="store_true",
        help="Use simplified viseme set (fewer visemes)",
    )

    parser.add_argument(
        "--no-visualization",
        action="store_true",
        help="Don't show timeline visualization",
    )

    parser.add_argument(
        "--list-voices", action="store_true", help="List available voices and exit"
    )

    args = parser.parse_args()

    # List voices
    if args.list_voices:
        print("Available Piper voices:")
        voices = PiperTTSEngine.list_available_voices()
        if voices:
            for voice in voices:
                print(f"  - {voice}")
        else:
            print("  No voices found or Piper not installed")
        return

    # Check text
    if not args.text:
        parser.error("Text is required (unless using --list-voices)")

    print("=" * 80)
    print("Piper TTS Demo - Phoneme/Viseme Output")
    print("=" * 80)
    print(f"\nText: {args.text}")
    print(f"Language: {args.language}")
    print(f"Simplified visemes: {args.simplified}")

    # Initialize TTS engine
    print("\nInitializing TTS engine...")
    engine = PiperTTSEngine(
        model_path=args.model,
        language=args.language,
        speaker=args.speaker,
        use_simplified_visemes=args.simplified,
    )

    # Synthesize
    print("Synthesizing speech...")
    try:
        if args.output:
            result = engine.synthesize_to_file(
                args.text, args.output, include_json=True
            )
            print(f"\nSaved audio to: {args.output}")
            print(f"Saved phoneme data to: {Path(args.output).with_suffix('.json')}")
        else:
            result = engine.synthesize(args.text)
            print("\nSynthesis complete (audio not saved)")

        # Display results
        print_phoneme_timeline(result)

        if not args.no_visualization:
            visualize_timeline(result)

        # Summary
        print("\n" + "=" * 80)
        print("Summary")
        print("=" * 80)
        print(f"Total phonemes: {len(result.phonemes)}")
        unique_visemes = set(p.viseme for p in result.phonemes)
        print(f"Unique visemes: {len(unique_visemes)}")
        print(f"Viseme list: {', '.join(sorted(unique_visemes))}")
        print("=" * 80)

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        print("\nTroubleshooting:")
        print("1. Make sure Piper TTS is installed:")
        print("   pip install piper-tts")
        print("2. Or download from: https://github.com/rhasspy/piper")
        print("3. Check if piper is in your PATH:")
        print("   piper --version")
        sys.exit(1)


if __name__ == "__main__":
    main()
