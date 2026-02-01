"""
Emotion Detection Module
Analyzes text to detect emotional content and intensity
Supports Sindhi, Urdu, and English text
"""

import logging
import re
from typing import Dict, Tuple, List
from collections import Counter

logger = logging.getLogger(__name__)

class EmotionDetector:
    """
    Text-based emotion detection using keyword analysis and linguistic patterns
    """
    
    def __init__(self):
        # Emotion keywords in multiple languages
        self.emotion_keywords = {
            'happy': {
                'en': ['happy', 'joy', 'excited', 'wonderful', 'great', 'excellent', 
                       'love', 'amazing', 'fantastic', 'delighted', 'cheerful', 'glad'],
                'ur': ['خوش', 'خوشی', 'مسرور', 'محبت', 'بہت اچھا', 'شاندار', 'لذیذ'],
                'sd': ['خوش', 'خوشي', 'مسرور', 'پياري', 'سٺو', 'شاندار', 'عمدو']
            },
            'sad': {
                'en': ['sad', 'unhappy', 'depressed', 'disappointed', 'sorrow', 
                       'grief', 'miserable', 'gloomy', 'upset', 'heartbroken'],
                'ur': ['غمگین', 'اداس', 'مایوس', 'دکھی', 'رنجیدہ', 'افسردہ', 'غم'],
                'sd': ['اداس', 'غمگين', 'دکھي', 'مايوس', 'رنجيدو', 'پريشان']
            },
            'angry': {
                'en': ['angry', 'mad', 'furious', 'rage', 'annoyed', 'irritated', 
                       'frustrated', 'outraged', 'hostile', 'bitter'],
                'ur': ['ناراض', 'غصے', 'خفا', 'غضبناک', 'برہم', 'چڑچڑا', 'جھلاہٹ'],
                'sd': ['ناراض', 'ڪاوڙيل', 'چڙيل', 'غصي ۾', 'برهم']
            },
            'calm': {
                'en': ['calm', 'peaceful', 'serene', 'tranquil', 'relaxed', 
                       'comfortable', 'quiet', 'gentle', 'composed'],
                'ur': ['پرسکون', 'سکون', 'آرام', 'ٹھنڈا', 'خاموش', 'نرم'],
                'sd': ['پرسکون', 'سکون', 'آرام سان', 'شانت', 'خاموش']
            },
            'serious': {
                'en': ['serious', 'solemn', 'formal', 'grave', 'earnest'],
                'ur': ['سنجیدہ', 'سنگین', 'وقار', 'گمبھیر'],
                'sd': ['سنجيده', 'سنگين', 'وقار', 'گمڀير']
            },
            'excited': {
                'en': ['excited', 'thrilled', 'enthusiastic', 'energetic', 
                       'pumped', 'eager', 'passionate', 'dynamic'],
                'ur': ['جوش', 'پرجوش', 'جوشیلا', 'متحرک', 'سرگرم', 'عش'],
                'sd': ['جوش', 'جوشيلو', 'سرگرم', 'متحرڪ', 'متحمس']
            },
            'fearful': {
                'en': ['afraid', 'scared', 'frightened', 'anxious', 'worried', 
                       'nervous', 'terrified', 'panic', 'fear'],
                'ur': ['خوفزدہ', 'ڈرا', 'گھبرایا', 'پریشان', 'فکرمند', 'خوف'],
                'sd': ['خوفزدو', 'ڊڄل', 'گهٻرايل', 'پريشان', 'فڪرمند']
            }
        }
        
        # Punctuation intensity markers
        self.intensity_markers = {
            '!': 0.3,      # Exclamation adds excitement/emphasis
            '!!': 0.5,
            '!!!': 0.7,
            '?': 0.2,      # Question adds uncertainty
            '...': 0.15,   # Ellipsis adds thoughtfulness/sadness
        }
        
        # Sindhi-specific linguistic markers
        self.sindhi_markers = {
            'آهي': 'affirmative',
            'نه': 'negative',
            'ته': 'emphasis',
            'ڇو': 'question',
            'ڪيئن': 'question',
        }
        
        logger.info("Emotion Detector initialized")
    
    def detect_emotion(
        self, 
        text: str, 
        language: str = "en",
        return_scores: bool = False
    ) -> Tuple[str, float] | Dict[str, float]:
        """
        Detect primary emotion in text
        
        Args:
            text: Text to analyze
            language: Language code (en, ur, sd)
            return_scores: If True, return all emotion scores
        
        Returns:
            If return_scores=False: (emotion, confidence)
            If return_scores=True: Dict of all emotion scores
        """
        if not text or not text.strip():
            return ('neutral', 0.0) if not return_scores else {'neutral': 1.0}
        
        # Normalize language code
        lang_map = {
            'English': 'en',
            'Urdu': 'ur', 
            'Sindhi': 'sd',
            'en': 'en',
            'ur': 'ur',
            'sd': 'sd'
        }
        lang = lang_map.get(language, 'en')
        
        # Calculate emotion scores
        scores = {}
        text_lower = text.lower()
        
        # Count emotion keywords
        for emotion, keywords_by_lang in self.emotion_keywords.items():
            keywords = keywords_by_lang.get(lang, [])
            count = sum(1 for keyword in keywords if keyword in text)
            scores[emotion] = count
        
        # Add intensity from punctuation
        intensity_boost = 0.0
        for marker, boost in self.intensity_markers.items():
            if marker in text:
                intensity_boost += boost
        
        # Apply intensity boost to all emotions
        if intensity_boost > 0:
            for emotion in scores:
                if scores[emotion] > 0:
                    scores[emotion] += intensity_boost
        
        # Analyze sentence structure for Sindhi
        if lang == 'sd':
            sindhi_boost = self._analyze_sindhi_structure(text)
            for emotion, boost in sindhi_boost.items():
                scores[emotion] = scores.get(emotion, 0) + boost
        
        # Normalize scores
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        else:
            # No emotion detected, return neutral
            scores = {'neutral': 1.0}
        
        if return_scores:
            return scores
        
        # Return primary emotion and confidence
        if 'neutral' in scores and scores['neutral'] == 1.0:
            return ('neutral', 1.0)
        
        primary_emotion = max(scores.items(), key=lambda x: x[1])
        return primary_emotion
    
    def _analyze_sindhi_structure(self, text: str) -> Dict[str, float]:
        """
        Analyze Sindhi linguistic structure for emotion cues
        """
        boosts = {}
        
        # Check for emphatic markers
        if 'ته' in text or 'ئي' in text:
            boosts['excited'] = 0.2
        
        # Check for questions (uncertainty/curiosity)
        if 'ڇو' in text or 'ڪيئن' in text or 'ڪڏهن' in text:
            boosts['curious'] = 0.15
            boosts['excited'] = 0.1
        
        # Check for negations (sadness/disappointment)
        if 'نه' in text or 'ڪو نه' in text:
            boosts['sad'] = 0.15
        
        return boosts
    
    def detect_emotion_shifts(self, text: str, language: str = "en") -> List[Dict]:
        """
        Detect emotion changes throughout text
        
        Returns:
            List of segments with their emotions
        """
        # Split text into sentences
        sentences = self._split_sentences(text)
        
        emotion_segments = []
        for i, sentence in enumerate(sentences):
            emotion, confidence = self.detect_emotion(sentence, language)
            emotion_segments.append({
                'text': sentence,
                'emotion': emotion,
                'confidence': confidence,
                'position': i
            })
        
        return emotion_segments
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Split on common sentence delimiters
        sentences = re.split(r'[.!?؟۔\n]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def analyze_emotional_intensity(self, text: str, language: str = "en") -> float:
        """
        Analyze overall emotional intensity of text
        
        Returns:
            Intensity score from 0.0 (neutral) to 1.0 (very emotional)
        """
        scores = self.detect_emotion(text, language, return_scores=True)
        
        # Neutral shouldn't count toward intensity
        if 'neutral' in scores:
            del scores['neutral']
        
        if not scores:
            return 0.0
        
        # Calculate intensity as maximum emotion score
        intensity = max(scores.values()) if scores else 0.0
        
        # Boost intensity for multiple strong emotions
        strong_emotions = sum(1 for score in scores.values() if score > 0.3)
        if strong_emotions > 1:
            intensity = min(1.0, intensity * 1.2)
        
        return intensity
    
    def get_prosody_adjustments(
        self, 
        text: str, 
        language: str = "en"
    ) -> Dict[str, float]:
        """
        Get recommended prosody adjustments based on detected emotion
        
        Returns:
            Dictionary with speaking_rate, pitch_shift, and volume adjustments
        """
        emotion, confidence = self.detect_emotion(text, language)
        intensity = self.analyze_emotional_intensity(text, language)
        
        # Base adjustments by emotion
        adjustments = {
            'neutral': {
                'speaking_rate': 1.0,
                'pitch_shift': 1.0,
                'volume': 1.0
            },
            'happy': {
                'speaking_rate': 1.15,
                'pitch_shift': 1.2,
                'volume': 1.1
            },
            'sad': {
                'speaking_rate': 0.85,
                'pitch_shift': 0.9,
                'volume': 0.9
            },
            'serious': {
                'speaking_rate': 0.95,
                'pitch_shift': 0.95,
                'volume': 0.95
            },
            'angry': {
                'speaking_rate': 1.2,
                'pitch_shift': 1.15,
                'volume': 1.15
            },
            'calm': {
                'speaking_rate': 0.9,
                'pitch_shift': 0.95,
                'volume': 0.95
            },
            'excited': {
                'speaking_rate': 1.25,
                'pitch_shift': 1.3,
                'volume': 1.2
            },
            'fearful': {
                'speaking_rate': 1.1,
                'pitch_shift': 1.1,
                'volume': 0.85
            }
        }
        
        base = adjustments.get(emotion, adjustments['neutral'])
        
        # Scale adjustments by confidence and intensity
        factor = confidence * intensity
        
        result = {
            'speaking_rate': 1.0 + (base['speaking_rate'] - 1.0) * factor,
            'pitch_shift': 1.0 + (base['pitch_shift'] - 1.0) * factor,
            'volume': 1.0 + (base['volume'] - 1.0) * factor,
            'emotion': emotion,
            'confidence': confidence,
            'intensity': intensity
        }
        
        return result


class MultiModalEmotionDetector(EmotionDetector):
    """
    Extended emotion detector supporting audio analysis
    (Future enhancement for voice input emotion detection)
    """
    
    def __init__(self):
        super().__init__()
        self.audio_model_loaded = False
    
    def detect_from_audio(self, audio_data: bytes) -> Tuple[str, float]:
        """
        Detect emotion from audio data
        Placeholder for future audio-based emotion detection
        """
        # TODO: Implement audio emotion detection
        # Could use models like:
        # - wav2vec2 for emotion
        # - OpenSMILE features
        # - Custom trained model on emotional speech
        logger.warning("Audio emotion detection not yet implemented")
        return ('neutral', 0.0)
    
    def detect_multimodal(
        self, 
        text: str, 
        audio_data: bytes = None,
        language: str = "en"
    ) -> Dict:
        """
        Combine text and audio emotion detection
        """
        text_emotion, text_conf = self.detect_emotion(text, language)
        
        if audio_data and self.audio_model_loaded:
            audio_emotion, audio_conf = self.detect_from_audio(audio_data)
            
            # Weighted combination
            if text_conf > audio_conf:
                final_emotion = text_emotion
                final_conf = text_conf
            else:
                final_emotion = audio_emotion
                final_conf = audio_conf
        else:
            final_emotion = text_emotion
            final_conf = text_conf
        
        return {
            'emotion': final_emotion,
            'confidence': final_conf,
            'text_emotion': text_emotion,
            'text_confidence': text_conf
        }


# Factory function
def create_emotion_detector(multimodal: bool = False) -> EmotionDetector:
    """
    Create emotion detector
    
    Args:
        multimodal: Whether to use multimodal detection (text + audio)
    
    Returns:
        Emotion detector instance
    """
    if multimodal:
        return MultiModalEmotionDetector()
    else:
        return EmotionDetector()
