"""
FastAPI backend for Self-Hosted Voice Agent
Supports multi-language TTS with emotion detection (English, Urdu, Sindhi)
100% Self-hosted - No external API dependencies
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional

from tts_pipeline import TTSPipeline

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom modules (offline-only)
try:
    from universal_tts import create_universal_tts, UniversalTTSEngine
    UNIVERSAL_TTS_AVAILABLE = True
except ImportError as e:
    UNIVERSAL_TTS_AVAILABLE = False
    logger.warning(f"Universal TTS not available: {e}")

try:
    from emotion_detector import create_emotion_detector, EmotionDetector
    EMOTION_DETECTION_AVAILABLE = True
except ImportError as e:
    EMOTION_DETECTION_AVAILABLE = False
    logger.warning(f"Emotion detection not available: {e}")

# Load environment variables
load_dotenv()

app = FastAPI(title="Self-Hosted Voice Agent API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

# Initialize Universal TTS engine (primary - offline phoneme synthesis)
universal_tts_engine = None
if UNIVERSAL_TTS_AVAILABLE:
    try:
        universal_tts_engine = create_universal_tts()
        logger.info("✅ Universal TTS engine initialized (English, Urdu, Sindhi)")
    except Exception as e:
        logger.error(f"Failed to initialize Universal TTS: {e}")
        universal_tts_engine = None

# Initialize emotion detector
emotion_detector = None
if EMOTION_DETECTION_AVAILABLE:
    try:
        emotion_detector = create_emotion_detector(multimodal=False)
        logger.info("✅ Emotion detector initialized")
    except Exception as e:
        logger.error(f"Failed to initialize emotion detector: {e}")
        emotion_detector = None

# Initialize TTS pipeline
tts_pipeline = None
if universal_tts_engine:
    tts_pipeline = TTSPipeline(
        tts_engine=universal_tts_engine,
        emotion_detector=emotion_detector
    )

# Pydantic models
class TTSRequest(BaseModel):
    text: str
    language: str = "English"
    emotion: Optional[str] = None  # auto, neutral, happy, sad, calm, serious
    speaking_rate: Optional[float] = 1.0
    pitch_shift: Optional[float] = 1.0

# Language mapping
LANGUAGE_CODES = {
    "English": "en",
    "Urdu": "ur",
    "Sindhi": "sd"
}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Self-Hosted Voice Agent API",
        "languages": ["English", "Urdu", "Sindhi"],
        "features": {
            "universal_tts": universal_tts_engine is not None,
            "emotion_detection": emotion_detector is not None,
            "self_hosted": True,
            "no_external_apis": True
        }
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "backend": "online",
        "tts_engine": {
            "type": "phoneme",
            "available": universal_tts_engine is not None,
            "languages": ["English", "Urdu", "Sindhi"],
            "status": "ready" if universal_tts_engine else "unavailable"
        },
        "emotion_detection": {
            "available": emotion_detector is not None,
            "status": "ready" if emotion_detector else "unavailable"
        },
        "external_dependencies": {
            "required": False,
            "message": "100% self-hosted solution"
        }
    }

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech with emotion detection and prosody adjustment
    100% Self-hosted - No external API calls
    Supports English, Urdu, and Sindhi
    """
    try:
        if not universal_tts_engine or not tts_pipeline:
            raise HTTPException(
                status_code=503,
                detail="TTS engine not available. Please check server logs."
            )
        
        language_code = LANGUAGE_CODES.get(request.language, "en")
        
        logger.info(f"TTS request: {request.text[:50]}... in {request.language}")
        
        detected_emotion = request.emotion or "auto"
        speaking_rate = request.speaking_rate or 1.0
        pitch_shift = request.pitch_shift or 1.0
        
        logger.info(f"Using offline phoneme TTS for {request.language} with emotion: {detected_emotion}")
        audio_content, meta = tts_pipeline.synthesize(
            text=request.text,
            language=request.language,
            emotion=detected_emotion,
            speaking_rate=speaking_rate,
            pitch_shift=pitch_shift
        )
        provider = "phoneme_tts"
        audio_format = "wav"
        
        import base64
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        logger.info(f"TTS success: {len(audio_content)} bytes using {provider} ({audio_format})")
        return {
            "status": "success",
            "language": request.language,
            "audio_format": audio_format,
            "audio": audio_base64,
            "provider": provider,
            "engine": provider,
            "emotion": meta.get("emotion", detected_emotion),
            "emotion_confidence": meta.get("confidence", 0.0),
            "prosody": {
                "speaking_rate": speaking_rate,
                "pitch_shift": pitch_shift
            },
            "pipeline": {
                "normalized_text": meta.get("normalized_text"),
                "token_count": len(meta.get("tokens", []))
            },
            "message": f"Audio generated successfully with Self-Hosted {request.language} TTS"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

@app.post("/api/emotion/analyze")
async def analyze_emotion(request: dict):
    """
    Analyze emotion in text
    Returns detected emotion, confidence, and prosody recommendations
    """
    try:
        if not emotion_detector:
            raise HTTPException(
                status_code=503,
                detail="Emotion detection not available"
            )
        
        text = request.get("text", "")
        language = request.get("language", "English")
        
        if not text:
            raise HTTPException(status_code=400, detail="Text is required")
        
        language_code = LANGUAGE_CODES.get(language, "en")
        
        # Get detailed emotion analysis
        emotion_scores = emotion_detector.detect_emotion(
            text, 
            language_code, 
            return_scores=True
        )
        
        # Get primary emotion
        primary_emotion, confidence = emotion_detector.detect_emotion(
            text, 
            language_code
        )
        
        # Get prosody adjustments
        prosody = emotion_detector.get_prosody_adjustments(text, language_code)
        
        # Get intensity
        intensity = emotion_detector.analyze_emotional_intensity(text, language_code)
        
        # Detect emotion shifts (for longer texts)
        shifts = emotion_detector.detect_emotion_shifts(text, language_code)
        
        return {
            "status": "success",
            "primary_emotion": primary_emotion,
            "confidence": confidence,
            "intensity": intensity,
            "emotion_scores": emotion_scores,
            "prosody_recommendations": {
                "speaking_rate": prosody.get('speaking_rate', 1.0),
                "pitch_shift": prosody.get('pitch_shift', 1.0),
                "volume": prosody.get('volume', 1.0)
            },
            "emotion_shifts": shifts if len(shifts) > 1 else [],
            "language": language
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Emotion analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Emotion analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
