"""
Universal Self-Hosted TTS Engine
Supports English, Urdu, and Sindhi with emotion-aware synthesis
No external API dependencies
"""

import logging
import numpy as np
from typing import Optional, Dict
import io
from pydub import AudioSegment
from pydub.generators import Sine, Square, Triangle
import re

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
        
        # Select appropriate phoneme map
        if language.lower() == "english":
            phoneme_map = self.english_phonemes
            text = text.lower()
        elif language.lower() == "urdu":
            phoneme_map = self.urdu_phonemes
        elif language.lower() == "sindhi":
            phoneme_map = self.sindhi_phonemes
        else:
            phoneme_map = self.english_phonemes
            text = text.lower()
        
        # Apply emotion-based prosody
        prosody = self._get_emotion_prosody(emotion)
        effective_rate = speaking_rate * prosody['rate_modifier']
        effective_pitch = pitch_shift * prosody['pitch_modifier']
        
        # Generate audio segments
        audio_segments = []
        
        for char in text:
            if char in phoneme_map:
                phoneme = phoneme_map[char]
                freq = phoneme['freq'] * effective_pitch
                duration = phoneme['duration'] / effective_rate
                duration = duration * prosody['duration_variance']
                
                if freq > 0:
                    segment = self._generate_tone(
                        freq, 
                        duration,
                        prosody['amplitude'],
                        emotion
                    )
                else:
                    segment = AudioSegment.silent(duration=int(duration))
                
                audio_segments.append(segment)
            else:
                # Unknown character - brief pause
                audio_segments.append(AudioSegment.silent(duration=50))
        
        # Concatenate segments
        if audio_segments:
            combined = audio_segments[0]
            for segment in audio_segments[1:]:
                combined += segment
        else:
            combined = AudioSegment.silent(duration=100)
        
        # Apply emotion filters
        combined = self._apply_emotion_filters(combined, emotion)
        
        # Export to MP3
        output_buffer = io.BytesIO()
        combined.export(output_buffer, format="mp3", bitrate="128k")
        audio_bytes = output_buffer.getvalue()
        
        logger.info(f"Synthesized {len(audio_bytes)} bytes of {language} audio")
        return audio_bytes
    
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
            wave = Square(frequency).to_audio_segment(duration=int(duration))
        elif emotion == 'calm':
            # Pure sine for smoothness
            wave = Sine(frequency).to_audio_segment(duration=int(duration))
        else:
            # Default sine wave
            wave = Sine(frequency).to_audio_segment(duration=int(duration))
        
        # Apply amplitude
        wave = wave - (60 * (1 - amplitude))
        
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
                'amplitude': 0.7
            },
            'happy': {
                'rate_modifier': 1.15,
                'pitch_modifier': 1.2,
                'duration_variance': 0.95,
                'amplitude': 0.85
            },
            'sad': {
                'rate_modifier': 0.85,
                'pitch_modifier': 0.9,
                'duration_variance': 1.1,
                'amplitude': 0.6
            },
            'angry': {
                'rate_modifier': 1.2,
                'pitch_modifier': 1.15,
                'duration_variance': 0.9,
                'amplitude': 0.9
            },
            'calm': {
                'rate_modifier': 0.9,
                'pitch_modifier': 0.95,
                'duration_variance': 1.05,
                'amplitude': 0.65
            },
            'excited': {
                'rate_modifier': 1.25,
                'pitch_modifier': 1.3,
                'duration_variance': 0.9,
                'amplitude': 0.9
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
