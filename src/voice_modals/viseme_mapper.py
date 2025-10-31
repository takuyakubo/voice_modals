"""Phoneme to Viseme mapping for lip-sync animation."""

from typing import Dict


class VisemeMapper:
    """Maps phonemes to visemes for facial animation."""

    # Standard viseme set based on common 3D animation standards
    # Compatible with Unity, Unreal Engine, etc.
    PHONEME_TO_VISEME: Dict[str, str] = {
        # Silence
        "sil": "sil",
        "pau": "sil",
        # Vowels
        "a": "aa",  # Open mouth - "father"
        "aː": "aa",
        "ɑ": "aa",
        "ɑː": "aa",
        "e": "E",  # Mouth slightly open - "bed"
        "eː": "E",
        "ɛ": "E",
        "i": "I",  # Smile - "see"
        "iː": "I",
        "ɪ": "I",
        "o": "O",  # Round lips - "go"
        "oː": "O",
        "ɔ": "O",
        "ɔː": "O",
        "u": "U",  # Pucker lips - "blue"
        "uː": "U",
        "ʊ": "U",
        # Consonants - Bilabial (lips together)
        "p": "PP",
        "b": "PP",
        "m": "PP",
        # Consonants - Labiodental (teeth on lip)
        "f": "FF",
        "v": "FF",
        # Consonants - Dental/Alveolar (tongue)
        "t": "TH",
        "d": "TH",
        "s": "SS",
        "z": "SS",
        "θ": "TH",
        "ð": "TH",
        "n": "nn",
        "l": "nn",
        # Consonants - Post-alveolar
        "ʃ": "CH",
        "ʒ": "CH",
        "tʃ": "CH",
        "dʒ": "CH",
        "r": "RR",
        # Consonants - Velar
        "k": "kk",
        "g": "kk",
        "ŋ": "nn",
        # Consonants - Glottal
        "h": "DD",
        # Diphthongs
        "aɪ": "aa",
        "aʊ": "aa",
        "eɪ": "E",
        "oɪ": "O",
        "oʊ": "O",
        # Japanese specific
        "N": "nn",  # ん
        "Q": "kk",  # っ (glottal stop)
        "ɯ": "U",   # う
        "ɛː": "E",
        # Default fallback
        "": "sil",
    }

    # Simplified viseme set (fewer visemes, easier animation)
    SIMPLIFIED_VISEME_MAP: Dict[str, str] = {
        "aa": "A",   # Open mouth
        "E": "E",    # Medium open
        "I": "I",    # Smile
        "O": "O",    # Round
        "U": "U",    # Pucker
        "PP": "M",   # Lips closed
        "FF": "F",   # Teeth on lip
        "TH": "T",   # Tongue
        "SS": "S",   # Hiss
        "CH": "Ch",  # Sh sound
        "RR": "R",   # R sound
        "kk": "K",   # Back of mouth
        "nn": "N",   # Nasal
        "DD": "D",   # Default
        "sil": "Sil", # Silence
    }

    @classmethod
    def phoneme_to_viseme(cls, phoneme: str, simplified: bool = False) -> str:
        """
        Convert a phoneme to a viseme.

        Args:
            phoneme: Phoneme string (IPA or other notation)
            simplified: Use simplified viseme set

        Returns:
            Viseme identifier string
        """
        # Get base viseme
        viseme = cls.PHONEME_TO_VISEME.get(phoneme, "sil")

        # Convert to simplified if requested
        if simplified:
            viseme = cls.SIMPLIFIED_VISEME_MAP.get(viseme, "Sil")

        return viseme

    @classmethod
    def get_viseme_description(cls, viseme: str) -> str:
        """
        Get a human-readable description of a viseme.

        Args:
            viseme: Viseme identifier

        Returns:
            Description string
        """
        descriptions = {
            "sil": "Silence (neutral mouth)",
            "aa": "Open mouth (ah)",
            "E": "Medium open mouth (eh)",
            "I": "Smile (ee)",
            "O": "Round lips (oh)",
            "U": "Pucker lips (oo)",
            "PP": "Lips pressed together (p, b, m)",
            "FF": "Lower lip against upper teeth (f, v)",
            "TH": "Tongue between/behind teeth (th, t, d)",
            "SS": "Teeth together, hissing (s, z)",
            "CH": "Lips forward, teeth close (sh, ch)",
            "RR": "Lips slightly rounded (r)",
            "kk": "Back of mouth (k, g)",
            "nn": "Nasal (n, ng)",
            "DD": "Default consonant",
        }
        return descriptions.get(viseme, "Unknown viseme")

    @classmethod
    def get_all_visemes(cls, simplified: bool = False) -> list:
        """
        Get list of all possible visemes.

        Args:
            simplified: Use simplified set

        Returns:
            List of viseme identifiers
        """
        if simplified:
            return list(set(cls.SIMPLIFIED_VISEME_MAP.values()))
        else:
            return list(set(cls.PHONEME_TO_VISEME.values()))
