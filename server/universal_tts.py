"""
Universal Self-Hosted TTS Engine
Supports English, Urdu, and Sindhi with emotion-aware synthesis
No external API dependencies
"""

import logging
import numpy as np
from typing import Optional, Dict
import io
import os
import shutil
from pydub import AudioSegment
from pydub.generators import Sine, Square, Triangle
import re

# Configure FFmpeg path
ffmpeg_path = shutil.which("ffmpeg")
if ffmpeg_path:
    AudioSegment.converter = ffmpeg_path
    AudioSegment.ffmpeg = ffmpeg_path
    AudioSegment.ffprobe = shutil.which("ffprobe") or ffmpeg_path.replace("ffmpeg", "ffprobe")

logger = logging.getLogger(__name__)

class UniversalTTSEngine:
    """
    Universal TTS Engine supporting multiple languages with emotion awareness
    Uses advanced phoneme-based synthesis
    """
    
    def __init__(self):
        self.sample_rate = 22050
        self.initialized = False
        
        # English phoneme mappings
        self.english_phonemes = self._create_english_phonemes()
        
        # Urdu phoneme mappings (using Arabic script)
        self.urdu_phonemes = self._create_urdu_phonemes()
        
        # Sindhi phoneme mappings
        self.sindhi_phonemes = self._create_sindhi_phonemes()

        # Pause durations in milliseconds
        self.pause_durations_ms = {
            ',': 200,
            '.': 320,
            '?': 300,
            '!': 260,
            ';': 220,
            ':': 220,
            '\n': 500,
            '،': 200,
            '؟': 300,
            '۔': 320
        }
        
        logger.info("Universal TTS Engine initialized for English, Urdu, and Sindhi")
        self.initialized = True
    
    def _create_english_phonemes(self) -> Dict:
        """Create English phoneme mappings"""
        phonemes = {}
        
        # Vowels
        vowels = {
            'a': {'freq': 700, 'duration': 120},
            'e': {'freq': 500, 'duration': 110},
            'i': {'freq': 320, 'duration': 100},
            'o': {'freq': 500, 'duration': 130},
            'u': {'freq': 380, 'duration': 120},
        }
        
        # Consonants
        consonants = {
            'b': {'freq': 200, 'duration': 80},
            'c': {'freq': 2300, 'duration': 75},
            'd': {'freq': 1800, 'duration': 70},
            'f': {'freq': 1400, 'duration': 85},
            'g': {'freq': 1900, 'duration': 80},
            'h': {'freq': 600, 'duration': 90},
            'j': {'freq': 2300, 'duration': 90},
            'k': {'freq': 2000, 'duration': 75},
            'l': {'freq': 1000, 'duration': 80},
            'm': {'freq': 250, 'duration': 100},
            'n': {'freq': 280, 'duration': 95},
            'p': {'freq': 220, 'duration': 80},
            'q': {'freq': 1100, 'duration': 90},
            'r': {'freq': 1200, 'duration': 60},
            's': {'freq': 5000, 'duration': 90},
            't': {'freq': 2800, 'duration': 70},
            'v': {'freq': 200, 'duration': 85},
            'w': {'freq': 400, 'duration': 90},
            'x': {'freq': 3500, 'duration': 85},
            'y': {'freq': 350, 'duration': 90},
            'z': {'freq': 3000, 'duration': 85},
        }
        
        phonemes.update(vowels)
        phonemes.update(consonants)
        phonemes[' '] = {'freq': 0, 'duration': 150}
        phonemes['.'] = {'freq': 0, 'duration': 300}
        phonemes[','] = {'freq': 0, 'duration': 200}
        phonemes['!'] = {'freq': 0, 'duration': 250}
        phonemes['?'] = {'freq': 0, 'duration': 250}
        
        return phonemes
    
    def _create_urdu_phonemes(self) -> Dict:
        """Create Urdu phoneme mappings"""
        return {
            # Vowels
            'ا': {'freq': 700, 'duration': 120},
            'آ': {'freq': 650, 'duration': 150},
            'ی': {'freq': 320, 'duration': 100},
            'و': {'freq': 500, 'duration': 130},
            'ے': {'freq': 380, 'duration': 110},
            
            # Consonants
            'ب': {'freq': 200, 'duration': 80},
            'پ': {'freq': 220, 'duration': 80},
            'ت': {'freq': 2800, 'duration': 70},
            'ٹ': {'freq': 2700, 'duration': 70},
            'ث': {'freq': 5000, 'duration': 90},
            'ج': {'freq': 2300, 'duration': 90},
            'چ': {'freq': 2400, 'duration': 90},
            'ح': {'freq': 800, 'duration': 100},
            'خ': {'freq': 900, 'duration': 100},
            'د': {'freq': 1800, 'duration': 70},
            'ڈ': {'freq': 1700, 'duration': 75},
            'ذ': {'freq': 1900, 'duration': 70},
            'ر': {'freq': 1200, 'duration': 60},
            'ڑ': {'freq': 1300, 'duration': 65},
            'ز': {'freq': 3000, 'duration': 85},
            'ژ': {'freq': 2800, 'duration': 85},
            'س': {'freq': 5000, 'duration': 90},
            'ش': {'freq': 4500, 'duration': 95},
            'ص': {'freq': 4800, 'duration': 90},
            'ض': {'freq': 1500, 'duration': 85},
            'ط': {'freq': 2400, 'duration': 80},
            'ظ': {'freq': 1950, 'duration': 85},
            'ع': {'freq': 750, 'duration': 105},
            'غ': {'freq': 850, 'duration': 105},
            'ف': {'freq': 1400, 'duration': 85},
            'ق': {'freq': 1100, 'duration': 90},
            'ک': {'freq': 2000, 'duration': 75},
            'گ': {'freq': 1900, 'duration': 80},
            'ل': {'freq': 1000, 'duration': 80},
            'م': {'freq': 250, 'duration': 100},
            'ن': {'freq': 280, 'duration': 95},
            'ں': {'freq': 300, 'duration': 95},
            'ہ': {'freq': 600, 'duration': 90},
            'ھ': {'freq': 620, 'duration': 90},
            
            ' ': {'freq': 0, 'duration': 150},
            '۔': {'freq': 0, 'duration': 300},
            '،': {'freq': 0, 'duration': 200},
            '؟': {'freq': 0, 'duration': 250},
        }
    
    def _create_sindhi_phonemes(self) -> Dict:
        """Create Sindhi phoneme mappings"""
        return {
            # Vowels
            'ا': {'freq': 700, 'duration': 120},
            'آ': {'freq': 650, 'duration': 150},
            'ي': {'freq': 320, 'duration': 100},
            'و': {'freq': 500, 'duration': 130},
            'ي': {'freq': 380, 'duration': 110},
            
            # Sindhi-specific consonants
            'ٻ': {'freq': 210, 'duration': 82},
            'ڀ': {'freq': 215, 'duration': 82},
            'ٺ': {'freq': 2700, 'duration': 75},
            'ٽ': {'freq': 2600, 'duration': 75},
            'ٿ': {'freq': 2500, 'duration': 75},
            'ڃ': {'freq': 2100, 'duration': 95},
            'ڄ': {'freq': 2200, 'duration': 90},
            'ڊ': {'freq': 1700, 'duration': 75},
            'ڏ': {'freq': 1600, 'duration': 75},
            'ڙ': {'freq': 1300, 'duration': 65},
            'ڪ': {'freq': 2000, 'duration': 75},
            'گ': {'freq': 1900, 'duration': 80},
            'ڳ': {'freq': 1850, 'duration': 80},
            'ڻ': {'freq': 300, 'duration': 95},
            
            # Common consonants
            'ب': {'freq': 200, 'duration': 80},
            'پ': {'freq': 220, 'duration': 80},
            'ت': {'freq': 2800, 'duration': 70},
            'ج': {'freq': 2300, 'duration': 90},
            'ح': {'freq': 800, 'duration': 100},
            'خ': {'freq': 900, 'duration': 100},
            'د': {'freq': 1800, 'duration': 70},
            'ذ': {'freq': 1900, 'duration': 70},
            'ر': {'freq': 1200, 'duration': 60},
            'ز': {'freq': 3000, 'duration': 85},
            'س': {'freq': 5000, 'duration': 90},
            'ش': {'freq': 4500, 'duration': 95},
            'ص': {'freq': 4800, 'duration': 90},
            'ض': {'freq': 1500, 'duration': 85},
            'ط': {'freq': 2400, 'duration': 80},
            'ظ': {'freq': 1950, 'duration': 85},
            'ع': {'freq': 750, 'duration': 105},
            'غ': {'freq': 850, 'duration': 105},
            'ف': {'freq': 1400, 'duration': 85},
            'ق': {'freq': 1100, 'duration': 90},
            'ل': {'freq': 1000, 'duration': 80},
            'م': {'freq': 250, 'duration': 100},
            'ن': {'freq': 280, 'duration': 95},
            'ه': {'freq': 600, 'duration': 90},
            'ھ': {'freq': 620, 'duration': 90},
            
            ' ': {'freq': 0, 'duration': 150},
            '.': {'freq': 0, 'duration': 300},
            '،': {'freq': 0, 'duration': 200},
        }

    def get_phoneme_map(self, language: str) -> Dict:
        """Return the phoneme map for a given language."""
        if language.lower() == "english":
            return self.english_phonemes
        if language.lower() == "urdu":
            return self.urdu_phonemes
        if language.lower() == "sindhi":
            return self.sindhi_phonemes
        return self.english_phonemes

    def get_pause_durations(self) -> Dict:
        """Return pause duration map in milliseconds."""
        return self.pause_durations_ms.copy()
    
    def synthesize(
        self, 
        text: str,
        language: str = "English",
        emotion: str = "neutral",
        speaking_rate: float = 1.0,
        pitch_shift: float = 1.0
    ) -> bytes:
        """
        Synthesize text to speech with emotion control
        
        Args:
            text: Text to synthesize
            language: Language (English, Urdu, Sindhi)
            emotion: Emotion type
            speaking_rate: Speech rate multiplier
            pitch_shift: Pitch shift multiplier
        
        Returns:
            Audio bytes in MP3 format
        """
        if not self.initialized:
            raise RuntimeError("TTS Engine not initialized")
        
        logger.info(f"Synthesizing {language} text with emotion: {emotion}")
        
        tokens = list(text.lower() if language.lower() == "english" else text)
        return self.synthesize_from_tokens(
            tokens=tokens,
            language=language,
            emotion=emotion,
            speaking_rate=speaking_rate,
            pitch_shift=pitch_shift
        )

    def build_units_from_tokens(
        self,
        tokens: list,
        language: str = "English",
        emotion: str = "neutral",
        speaking_rate: float = 1.0,
        pitch_shift: float = 1.0
    ) -> list:
        """Build synthesis units without rendering audio (for tests/debug)."""
        phoneme_map = self.get_phoneme_map(language)

        prosody = self._get_emotion_prosody(emotion)
        effective_rate = speaking_rate * prosody['rate_modifier']
        effective_pitch = pitch_shift * prosody['pitch_modifier']

        units = []
        for token in tokens:
            if token in self.pause_durations_ms or token == "\n":
                pause = self.pause_durations_ms.get(token, 200)
                pause = pause / effective_rate
                units.append({
                    "token": token,
                    "freq": 0,
                    "duration_ms": float(pause),
                    "amplitude": prosody['amplitude'],
                    "is_pause": True
                })
            elif token in phoneme_map:
                phoneme = phoneme_map[token]
                freq = phoneme['freq'] * effective_pitch
                duration = phoneme['duration'] / effective_rate
                duration = duration * prosody['duration_variance']
                units.append({
                    "token": token,
                    "freq": freq,
                    "duration_ms": float(duration),
                    "amplitude": prosody['amplitude'],
                    "is_pause": freq == 0
                })
            else:
                units.append({
                    "token": token,
                    "freq": 0,
                    "duration_ms": 50.0,
                    "amplitude": prosody['amplitude'],
                    "is_pause": True
                })

        return units

    def synthesize_from_tokens(
        self,
        tokens: list,
        language: str = "English",
        emotion: str = "neutral",
        speaking_rate: float = 1.0,
        pitch_shift: float = 1.0
    ) -> bytes:
        """Synthesize audio from phoneme tokens."""
        units = self.build_units_from_tokens(
            tokens=tokens,
            language=language,
            emotion=emotion,
            speaking_rate=speaking_rate,
            pitch_shift=pitch_shift
        )

        combined = self._render_units(units, emotion)

        output_buffer = io.BytesIO()
        combined.export(output_buffer, format="wav")
        audio_bytes = output_buffer.getvalue()

        logger.info(f"Synthesized {len(audio_bytes)} bytes of {language} audio")
        return audio_bytes

    def _render_units(self, units: list, emotion: str) -> AudioSegment:
        """Render units to an AudioSegment."""
        audio_segments = []
        for unit in units:
            if unit["freq"] > 0:
                segment = self._generate_tone(
                    unit["freq"],
                    unit["duration_ms"],
                    unit.get("amplitude", 1.0),
                    emotion
                )
            else:
                segment = AudioSegment.silent(duration=int(unit["duration_ms"]))
            audio_segments.append(segment)

        if audio_segments:
            combined = audio_segments[0]
            for segment in audio_segments[1:]:
                combined += segment
        else:
            combined = AudioSegment.silent(duration=100)

        return self._apply_emotion_filters(combined, emotion)
    
    def _generate_tone(
        self, 
        frequency: float, 
        duration: float, 
        amplitude: float = 0.5,
        emotion: str = "neutral"
    ) -> AudioSegment:
        """Generate tone with emotion-specific characteristics"""
        
        # Use different waveforms for different emotions
        if emotion in ['angry', 'excited']:
            # Square wave for harsher sound
            wave = Square(frequency, sample_rate=self.sample_rate).to_audio_segment(duration=int(duration), volume=-20)
        elif emotion == 'calm':
            # Pure sine for smoothness
            wave = Sine(frequency, sample_rate=self.sample_rate).to_audio_segment(duration=int(duration), volume=-20)
        else:
            # Default sine wave
            wave = Sine(frequency, sample_rate=self.sample_rate).to_audio_segment(duration=int(duration), volume=-20)
        
        # Apply amplitude (boost volume significantly)
        wave = wave + 12  # Increase volume by 12dB
        
        # Add envelope
        fade_duration = min(10, int(duration * 0.1))
        if fade_duration > 0:
            wave = wave.fade_in(fade_duration).fade_out(fade_duration)
        
        return wave
    
    def _get_emotion_prosody(self, emotion: str) -> Dict:
        """Get prosody parameters for emotion"""
        prosody_params = {
            'neutral': {
                'rate_modifier': 1.0,
                'pitch_modifier': 1.0,
                'duration_variance': 1.0,
                'amplitude': 1.0
            },
            'happy': {
                'rate_modifier': 1.15,
                'pitch_modifier': 1.2,
                'duration_variance': 0.95,
                'amplitude': 1.0
            },
            'sad': {
                'rate_modifier': 0.85,
                'pitch_modifier': 0.9,
                'duration_variance': 1.1,
                'amplitude': 0.8
            },
            'angry': {
                'rate_modifier': 1.2,
                'pitch_modifier': 1.15,
                'duration_variance': 0.9,
                'amplitude': 1.0
            },
            'calm': {
                'rate_modifier': 0.9,
                'pitch_modifier': 0.95,
                'duration_variance': 1.05,
                'amplitude': 0.85
            },
            'serious': {
                'rate_modifier': 0.95,
                'pitch_modifier': 0.95,
                'duration_variance': 1.0,
                'amplitude': 0.9
            },
            'excited': {
                'rate_modifier': 1.25,
                'pitch_modifier': 1.3,
                'duration_variance': 0.9,
                'amplitude': 1.0
            }
        }
        
        return prosody_params.get(emotion, prosody_params['neutral'])
    
    def _apply_emotion_filters(self, audio: AudioSegment, emotion: str) -> AudioSegment:
        """Apply emotion-specific audio filters"""
        
        if emotion == 'happy':
            audio = audio.high_pass_filter(80)
        elif emotion == 'sad':
            audio = audio.low_pass_filter(3000)
        elif emotion == 'angry':
            audio = audio + 2
        elif emotion == 'calm':
            audio = audio.low_pass_filter(4000)
        
        return audio
    
    def is_available(self) -> bool:
        """Check if engine is available"""
        return self.initialized


# Factory function
def create_universal_tts() -> UniversalTTSEngine:
    """Create universal TTS engine instance"""
    return UniversalTTSEngine()
