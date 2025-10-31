"""Text-to-Speech engine using Piper TTS with phoneme/viseme support."""

import json
import subprocess
import tempfile
import wave
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np

from .viseme_mapper import VisemeMapper


@dataclass
class PhonemeEvent:
    """A phoneme event with timing information."""

    start: float  # Start time in seconds
    end: float  # End time in seconds
    phoneme: str  # Phoneme string
    viseme: str  # Corresponding viseme


@dataclass
class TTSResult:
    """Result of text-to-speech synthesis."""

    audio: np.ndarray  # Audio samples (float32, 16kHz or 22kHz)
    sample_rate: int  # Audio sample rate
    duration: float  # Total duration in seconds
    phonemes: List[PhonemeEvent]  # Phoneme timeline
    text: str  # Original text


class PiperTTSEngine:
    """Text-to-Speech engine using Piper with phoneme/viseme output."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        language: str = "en-us",
        speaker: Optional[str] = None,
        use_simplified_visemes: bool = True,
    ):
        """
        Initialize Piper TTS engine.

        Args:
            model_path: Path to Piper model file (.onnx)
            language: Language code (e.g., 'en-us', 'ja')
            speaker: Speaker name/ID if multi-speaker model
            use_simplified_visemes: Use simplified viseme set
        """
        self.model_path = model_path
        self.language = language
        self.speaker = speaker
        self.use_simplified_visemes = use_simplified_visemes
        self.viseme_mapper = VisemeMapper()

        # Check if piper is installed
        try:
            result = subprocess.run(
                ["piper", "--version"], capture_output=True, text=True, check=True
            )
            print(f"Piper TTS version: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Warning: Piper TTS not found in PATH")
            print("Install with: pip install piper-tts")
            print("Or download from: https://github.com/rhasspy/piper")

    def synthesize(
        self, text: str, output_file: Optional[str] = None
    ) -> TTSResult:
        """
        Synthesize speech from text with phoneme/viseme information.

        Args:
            text: Input text to synthesize
            output_file: Optional output WAV file path

        Returns:
            TTSResult with audio and phoneme timeline
        """
        # Create temporary files if needed
        temp_audio = output_file or tempfile.mktemp(suffix=".wav")
        temp_phonemes = tempfile.mktemp(suffix=".json")

        try:
            # Build piper command
            cmd = ["piper"]

            if self.model_path:
                cmd.extend(["--model", self.model_path])

            # Output phoneme JSON
            cmd.extend(["--json-input", "--output_file", temp_audio])

            # Prepare input JSON
            input_data = {"text": text}
            if self.speaker:
                input_data["speaker"] = self.speaker

            input_json = json.dumps(input_data)

            # Run piper
            result = subprocess.run(
                cmd,
                input=input_json,
                capture_output=True,
                text=True,
                check=True,
            )

            # Parse phoneme output from stdout
            phonemes = self._parse_piper_output(result.stdout)

            # Load audio
            audio, sample_rate = self._load_audio(temp_audio)

            # Calculate duration
            duration = len(audio) / sample_rate

            # Convert phonemes to visemes
            phoneme_events = self._create_phoneme_events(phonemes, duration)

            return TTSResult(
                audio=audio,
                sample_rate=sample_rate,
                duration=duration,
                phonemes=phoneme_events,
                text=text,
            )

        except subprocess.CalledProcessError as e:
            print(f"Piper TTS error: {e.stderr}")
            raise
        except Exception as e:
            print(f"TTS synthesis error: {e}")
            raise
        finally:
            # Cleanup temp files
            if not output_file and Path(temp_audio).exists():
                Path(temp_audio).unlink()
            if Path(temp_phonemes).exists():
                Path(temp_phonemes).unlink()

    def _parse_piper_output(self, output: str) -> List[dict]:
        """
        Parse Piper's phoneme output.

        Args:
            output: Piper stdout containing phoneme info

        Returns:
            List of phoneme dictionaries
        """
        phonemes = []
        try:
            # Piper outputs JSON lines
            for line in output.strip().split("\n"):
                if line.strip():
                    data = json.loads(line)
                    if "phonemes" in data:
                        phonemes.extend(data["phonemes"])
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse phoneme data: {e}")

        return phonemes

    def _load_audio(self, audio_file: str) -> Tuple[np.ndarray, int]:
        """
        Load audio from WAV file.

        Args:
            audio_file: Path to WAV file

        Returns:
            Tuple of (audio samples, sample rate)
        """
        with wave.open(audio_file, "rb") as wf:
            sample_rate = wf.getframerate()
            frames = wf.readframes(wf.getnframes())

            # Convert to numpy array
            audio = np.frombuffer(frames, dtype=np.int16)
            # Normalize to float32 [-1.0, 1.0]
            audio = audio.astype(np.float32) / 32768.0

            return audio, sample_rate

    def _create_phoneme_events(
        self, phonemes: List[dict], total_duration: float
    ) -> List[PhonemeEvent]:
        """
        Create phoneme events with timing and viseme mapping.

        Args:
            phonemes: List of phoneme dictionaries from Piper
            total_duration: Total audio duration

        Returns:
            List of PhonemeEvent objects
        """
        events = []

        if not phonemes:
            # If no phonemes, create a single silence event
            return [
                PhonemeEvent(
                    start=0.0,
                    end=total_duration,
                    phoneme="sil",
                    viseme=self.viseme_mapper.phoneme_to_viseme(
                        "sil", self.use_simplified_visemes
                    ),
                )
            ]

        # Calculate timing for each phoneme
        for i, phoneme_data in enumerate(phonemes):
            phoneme = phoneme_data.get("phoneme", "")

            # Estimate timing (simple equal distribution for now)
            # In real Piper output, these would come from the model
            start = (i / len(phonemes)) * total_duration
            end = ((i + 1) / len(phonemes)) * total_duration

            # Map to viseme
            viseme = self.viseme_mapper.phoneme_to_viseme(
                phoneme, self.use_simplified_visemes
            )

            events.append(
                PhonemeEvent(start=start, end=end, phoneme=phoneme, viseme=viseme)
            )

        return events

    def synthesize_to_file(
        self, text: str, output_file: str, include_json: bool = True
    ) -> TTSResult:
        """
        Synthesize speech and save to file.

        Args:
            text: Input text
            output_file: Output WAV file path
            include_json: Also save phoneme/viseme data as JSON

        Returns:
            TTSResult object
        """
        result = self.synthesize(text, output_file)

        # Save phoneme/viseme data as JSON
        if include_json:
            json_file = Path(output_file).with_suffix(".json")
            data = {
                "text": result.text,
                "duration": result.duration,
                "sample_rate": result.sample_rate,
                "phonemes": [
                    {
                        "start": p.start,
                        "end": p.end,
                        "phoneme": p.phoneme,
                        "viseme": p.viseme,
                    }
                    for p in result.phonemes
                ],
            }
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            print(f"Saved phoneme data to: {json_file}")

        return result

    @staticmethod
    def list_available_voices() -> List[str]:
        """
        List available Piper voices.

        Returns:
            List of voice names
        """
        try:
            result = subprocess.run(
                ["piper", "--list-voices"], capture_output=True, text=True, check=True
            )
            return result.stdout.strip().split("\n")
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []
