"""
Phoneme TTS Pipeline
Text -> Normalize -> G2P -> Emotion -> Prosody -> Phoneme Synthesis -> WAV
"""

from typing import Dict, Optional, List, Tuple

from text_normalizer import TextNormalizer
from g2p import G2PConverter
from prosody import ProsodyMapper
from universal_tts import UniversalTTSEngine
from emotion_detector import EmotionDetector

class TTSPipeline:
    def __init__(
        self,
        tts_engine: UniversalTTSEngine,
        emotion_detector: Optional[EmotionDetector] = None
    ):
        self.normalizer = TextNormalizer()
        self.prosody = ProsodyMapper()
        self.tts_engine = tts_engine
        self.emotion_detector = emotion_detector
        self.g2p = G2PConverter(self.prosody.get_pause_map())

    def synthesize(
        self,
        text: str,
        language: str = "English",
        emotion: Optional[str] = None,
        speaking_rate: float = 1.0,
        pitch_shift: float = 1.0
    ) -> Tuple[bytes, Dict]:
        normalized = self.normalizer.normalize(text, language)
        phoneme_map = self.tts_engine.get_phoneme_map(language)
        tokens = self.g2p.to_tokens(normalized, phoneme_map)

        detected_emotion = emotion or "auto"
        prosody_adjustments = {}

        if self.emotion_detector and (not emotion or emotion == "auto"):
            prosody_adjustments = self.emotion_detector.get_prosody_adjustments(
                normalized,
                self._lang_code(language)
            )
            detected_emotion = prosody_adjustments.get("emotion", "neutral")

        if not detected_emotion:
            detected_emotion = "neutral"

        prosody_adjustments = self.prosody.merge_emotion_prosody(
            prosody_adjustments,
            detected_emotion
        )

        speaking_rate = speaking_rate or prosody_adjustments.get("speaking_rate", 1.0)
        pitch_shift = pitch_shift or prosody_adjustments.get("pitch_shift", 1.0)

        audio_bytes = self.tts_engine.synthesize_from_tokens(
            tokens=tokens,
            language=language,
            emotion=detected_emotion,
            speaking_rate=speaking_rate,
            pitch_shift=pitch_shift
        )

        meta = {
            "normalized_text": normalized,
            "tokens": tokens,
            "emotion": detected_emotion,
            "speaking_rate": speaking_rate,
            "pitch_shift": pitch_shift,
            "confidence": prosody_adjustments.get("confidence", 0.0),
            "intensity": prosody_adjustments.get("intensity", 0.0)
        }

        return audio_bytes, meta

    def debug_units(
        self,
        text: str,
        language: str = "English",
        emotion: Optional[str] = None,
        speaking_rate: float = 1.0,
        pitch_shift: float = 1.0
    ) -> List[Dict]:
        normalized = self.normalizer.normalize(text, language)
        phoneme_map = self.tts_engine.get_phoneme_map(language)
        tokens = self.g2p.to_tokens(normalized, phoneme_map)

        detected_emotion = emotion or "neutral"
        prosody_adjustments = {}

        if self.emotion_detector and (not emotion or emotion == "auto"):
            prosody_adjustments = self.emotion_detector.get_prosody_adjustments(
                normalized,
                self._lang_code(language)
            )
            detected_emotion = prosody_adjustments.get("emotion", "neutral")

        if not detected_emotion:
            detected_emotion = "neutral"

        return self.tts_engine.build_units_from_tokens(
            tokens=tokens,
            language=language,
            emotion=detected_emotion,
            speaking_rate=speaking_rate,
            pitch_shift=pitch_shift
        )

    def _lang_code(self, language: str) -> str:
        return {
            "English": "en",
            "Urdu": "ur",
            "Sindhi": "sd",
            "en": "en",
            "ur": "ur",
            "sd": "sd"
        }.get(language, "en")
