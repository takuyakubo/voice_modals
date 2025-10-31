"""Example: Export TTS phonemes for animation software (Unity, Unreal, etc.)."""

import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voice_modals import PiperTTSEngine, VisemeMapper


def export_for_unity(result, output_file: str):
    """
    Export phoneme data in Unity-compatible format.

    Unity typically uses OVR Lip Sync or similar systems.
    """
    unity_data = {
        "version": "1.0",
        "text": result.text,
        "duration": result.duration,
        "frameRate": 30,  # Assume 30fps animation
        "visemeFrames": [],
    }

    # Convert to frame-based timeline
    fps = 30
    for event in result.phonemes:
        start_frame = int(event.start * fps)
        end_frame = int(event.end * fps)

        unity_data["visemeFrames"].append(
            {
                "startFrame": start_frame,
                "endFrame": end_frame,
                "viseme": event.viseme,
                "phoneme": event.phoneme,
            }
        )

    # Save
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(unity_data, f, indent=2)

    print(f"✓ Exported Unity-compatible data to: {output_file}")


def export_for_blender(result, output_file: str):
    """
    Export phoneme data for Blender shape key animation.

    Blender uses shape keys for facial animation.
    """
    blender_data = {
        "text": result.text,
        "duration": result.duration,
        "fps": 24,  # Blender default
        "shapeKeys": [],
    }

    # Convert visemes to shape key influences
    fps = 24
    for event in result.phonemes:
        start_frame = int(event.start * fps)
        end_frame = int(event.end * fps)

        # Each viseme corresponds to a shape key
        blender_data["shapeKeys"].append(
            {
                "frame_start": start_frame,
                "frame_end": end_frame,
                "key_name": f"viseme_{event.viseme}",
                "influence": 1.0,
                "phoneme": event.phoneme,
            }
        )

    # Save
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(blender_data, f, indent=2)

    print(f"✓ Exported Blender-compatible data to: {output_file}")


def export_subtitles(result, output_file: str):
    """
    Export as SRT subtitle format.

    Useful for video editing.
    """
    srt_content = []

    # Group phonemes into words (simplified)
    # In real implementation, you'd need word boundaries
    subtitle_index = 1
    current_text = ""
    start_time = 0

    for i, event in enumerate(result.phonemes):
        current_text += event.phoneme

        # Create subtitle every 2 seconds or at end
        if event.end - start_time > 2.0 or i == len(result.phonemes) - 1:
            # Format timestamps for SRT (HH:MM:SS,mmm)
            start_srt = format_srt_time(start_time)
            end_srt = format_srt_time(event.end)

            srt_content.append(f"{subtitle_index}")
            srt_content.append(f"{start_srt} --> {end_srt}")
            srt_content.append(result.text)  # Original text
            srt_content.append("")  # Blank line

            subtitle_index += 1
            start_time = event.end
            current_text = ""

    # Save
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_content))

    print(f"✓ Exported SRT subtitles to: {output_file}")


def format_srt_time(seconds: float) -> str:
    """Format seconds as SRT timestamp (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def main():
    """Export TTS data for animation software."""
    print("=" * 80)
    print("TTS Animation Export Example")
    print("=" * 80)

    # Initialize TTS
    print("\nInitializing Piper TTS...")
    engine = PiperTTSEngine(language="en-us", use_simplified_visemes=True)

    # Synthesize speech
    text = "Welcome to the animation export demo. This text will be converted to lip sync data."
    print(f"\nText: {text}\n")

    print("Synthesizing speech...")
    result = engine.synthesize_to_file(text, "animation_demo.wav")

    print(f"\n✓ Audio saved to: animation_demo.wav")
    print(f"Duration: {result.duration:.2f}s")
    print(f"Phonemes: {len(result.phonemes)}")

    # Export in multiple formats
    print("\nExporting in multiple formats...")

    export_for_unity(result, "animation_demo_unity.json")
    export_for_blender(result, "animation_demo_blender.json")
    export_subtitles(result, "animation_demo.srt")

    print("\n" + "=" * 80)
    print("Export Complete!")
    print("=" * 80)
    print("\nFiles created:")
    print("  - animation_demo.wav (audio)")
    print("  - animation_demo_unity.json (Unity format)")
    print("  - animation_demo_blender.json (Blender format)")
    print("  - animation_demo.srt (subtitles)")
    print("\nYou can now import these files into your animation software!")
    print("=" * 80)


if __name__ == "__main__":
    main()
