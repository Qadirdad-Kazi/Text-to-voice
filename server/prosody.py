"""
Prosody Mapping Module
Emotion-aware prosody mapping without external dependencies
"""

from typing import Dict

class ProsodyMapper:
    """
    Combines emotion rules with pause/intonation defaults.
    """

    DEFAULT_PAUSE_MS = {
        ",": 200,
        ".": 320,
        "?": 300,
        "!": 260,
        ";": 220,
        ":": 220,
        "\n": 500,
    }

    def get_pause_map(self) -> Dict[str, int]:
        return self.DEFAULT_PAUSE_MS.copy()

    def merge_emotion_prosody(self, base: Dict[str, float], emotion: str) -> Dict[str, float]:
        # Ensure minimal defaults even if emotion detection returns none
        if not base:
            base = {}

        base.setdefault("speaking_rate", 1.0)
        base.setdefault("pitch_shift", 1.0)
        base.setdefault("volume", 1.0)

        # Extend to support "serious" in addition to existing emotions
        if emotion == "serious":
            base["speaking_rate"] = min(base["speaking_rate"], 0.95)
            base["pitch_shift"] = min(base["pitch_shift"], 0.95)
            base["volume"] = min(base["volume"], 1.0)

        return base
