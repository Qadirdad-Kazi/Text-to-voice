"""
FastAPI backend for LiveKit Voice Agent
Supports multi-language TTS/STT (English, Urdu, Sindhi)
"""

import os
import logging
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import asyncio
from typing import Optional

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from livekit import api
    LIVEKIT_AVAILABLE = True
except ImportError:
    LIVEKIT_AVAILABLE = False
    logger.warning("LiveKit not installed. Token generation will be disabled.")

import openai

# Load environment variables
load_dotenv()

app = FastAPI(title="LiveKit Voice Agent API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")
# Do not hardcode a LiveKit URL; require configuration via env var when deploying.
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
UPLIFT_API_KEY = os.getenv("UPLIFT_API_KEY")
# Optional override for Uplift API base URL (keeps the endpoint configurable)
UPLIFT_API_URL = os.getenv("UPLIFT_API_URL", "https://api.upliftai.org")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
USE_UPLIFT_TTS = os.getenv("USE_UPLIFT_TTS", "false").lower() == "true"

# Configure OpenAI
openai.api_key = OPENAI_API_KEY
if OPENAI_BASE_URL:
    try:
        openai.base_url = OPENAI_BASE_URL
        logger.info(f"Using custom OpenAI base URL: {OPENAI_BASE_URL}")
    except Exception:
        logger.warning("Failed to set OpenAI base URL; proceeding with default")

# Track if a key is present; warn if format is unusual but don't block usage
OPENAI_KEY_PRESENT = bool(OPENAI_API_KEY)
OPENAI_FORMAT_OK = bool(OPENAI_API_KEY and OPENAI_API_KEY.startswith("sk-"))

# Supported OpenAI voices
OPENAI_VOICES = {"alloy", "nova", "shimmer"}

def normalize_openai_voice(requested_voice: Optional[str], language: str) -> str:
    if requested_voice and requested_voice in OPENAI_VOICES:
        return requested_voice
    mapped = VOICE_MAPPING.get(language)
    if mapped in OPENAI_VOICES:
        return mapped
    return "alloy"

def _mask_key(k: Optional[str]) -> str:
    if not k:
        return "<none>"
    if len(k) <= 8:
        return "*" * len(k)
    return k[:6] + "…" + k[-4:]

if not OPENAI_KEY_PRESENT:
    logger.warning("OPENAI_API_KEY is missing. Set it in server/.env to enable OpenAI features.")
else:
    if not OPENAI_FORMAT_OK:
        logger.warning("OPENAI_API_KEY has an unexpected format. Proceeding anyway, but authentication may fail.")
    logger.info(f"OpenAI key present: {_mask_key(OPENAI_API_KEY)}")

# Initialize Uplift AI client if enabled
uplift_client = None
if USE_UPLIFT_TTS and UPLIFT_API_KEY:
    try:
        from uplift_client import UpliftWebSocketClient
        uplift_client = UpliftWebSocketClient(UPLIFT_API_KEY)
        logger.info("Uplift AI WebSocket TTS enabled")
    except ImportError:
        uplift_client = None
        logger.warning("Uplift WebSocket client not installed; realtime Uplift TTS disabled. Using REST fallback when available.")

# Pydantic models
class TTSRequest(BaseModel):
    text: str
    language: str = "English"
    voice: Optional[str] = None

class STTRequest(BaseModel):
    audio_data: str  # Base64 encoded audio
    language: str = "English"

class ChatRequest(BaseModel):
    message: str
    language: str = "English"
    history: list = []

class TokenRequest(BaseModel):
    room_name: str
    participant_name: str
    language: str = "English"

# Language mapping
LANGUAGE_CODES = {
    "English": "en",
    "Urdu": "ur",
    "Sindhi": "sd"
}

VOICE_MAPPING = {
    "English": "alloy",  # OpenAI TTS voice
    "Urdu": "nova",      # OpenAI TTS voice
    "Sindhi": "shimmer"  # OpenAI TTS voice (fallback)
}

# Uplift AI voice mapping (when USE_UPLIFT_TTS=true)
# Based on https://docs.upliftai.org/introduction#javascript
UPLIFT_VOICE_MAPPING = {
    "English": "v_8eelc901",   # Info/Education voice
    "Urdu": "v_8eelc901",       # Info/Education voice (optimized for Urdu)
    "Sindhi": "v_8eelc901"      # Info/Education voice
}

# Alternative voices you can use:
# "v_30s70t3a" - Nostalgic News voice
# "v_yypgzenx" - Dada Jee (storytelling voice)
# "v_kwmp7zxt" - Gen Z voice (under development)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "LiveKit Voice Agent API",
        "languages": ["English", "Urdu", "Sindhi"],
        "uplift_tts_enabled": USE_UPLIFT_TTS and uplift_client is not None,
        "openai_configured": OPENAI_KEY_PRESENT
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "backend": "online",
        "uplift_ai": {
            "enabled": USE_UPLIFT_TTS,
            "client_initialized": uplift_client is not None,
            "connected": uplift_client.connected if uplift_client else False,
            "ready": bool(USE_UPLIFT_TTS and UPLIFT_API_KEY)
        },
        "openai": {
            "configured": OPENAI_KEY_PRESENT,
            "base_url": OPENAI_BASE_URL or "https://api.openai.com/v1"
        },
        "livekit": {
            "available": LIVEKIT_AVAILABLE,
            "configured": bool(LIVEKIT_API_KEY and LIVEKIT_API_KEY != "placeholder")
        }
    }

@app.post("/api/token")
async def create_token(request: TokenRequest):
    """
    Generate LiveKit access token for client connection
    """
    try:
        if not LIVEKIT_AVAILABLE:
            raise HTTPException(status_code=501, detail="LiveKit not installed. Please install livekit package.")
        
        if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
            raise HTTPException(status_code=500, detail="LiveKit credentials not configured")
        
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        token.with_identity(request.participant_name)
        token.with_name(request.participant_name)
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=request.room_name,
            can_publish=True,
            can_subscribe=True,
        ))
        
        jwt_token = token.to_jwt()
        
        return {
            "token": jwt_token,
            "url": LIVEKIT_URL,
            "room_name": request.room_name,
            "language": request.language
        }
    except Exception as e:
        logger.error(f"Token generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech using Uplift AI WebSocket TTS or OpenAI TTS
    Supports English, Urdu, and Sindhi
    Uplift AI provides ~300ms first chunk latency for better real-time performance
    """
    try:
        language_code = LANGUAGE_CODES.get(request.language, "en")
        
        logger.info(f"TTS request: {request.text[:50]}... in {request.language}")
        
        # Use Uplift AI REST API if enabled
        if USE_UPLIFT_TTS and UPLIFT_API_KEY:
            # Use provided voice ID, or fall back to language-based default
            voice_id = request.voice if request.voice else UPLIFT_VOICE_MAPPING.get(request.language, "v_8eelc901")
            
            try:
                import aiohttp
                
                logger.info(f"Synthesizing with Uplift AI REST API voice: {voice_id}")
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{UPLIFT_API_URL}/v1/synthesis/text-to-speech",
                        headers={
                            'Authorization': f'Bearer {UPLIFT_API_KEY}',
                            'Content-Type': 'application/json'
                        },
                        json={
                            "voiceId": voice_id,
                            "text": request.text,
                            "outputFormat": "MP3_22050_128"
                        }
                    ) as response:
                        if response.status == 200:
                            audio_content = await response.read()
                            audio_duration = response.headers.get('x-uplift-ai-audio-duration')
                            
                            import base64
                            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
                            
                            logger.info(f"Uplift AI TTS success: {len(audio_content)} bytes, duration: {audio_duration}ms")
                            return {
                                "status": "success",
                                "language": request.language,
                                "audio_format": "mp3",
                                "audio": audio_base64,
                                "provider": "uplift",
                                "duration_ms": audio_duration,
                                "message": "Audio generated successfully with Uplift AI"
                            }
                        else:
                            error_text = await response.text()
                            raise Exception(f"Uplift API returned {response.status}: {error_text}")
                    
            except Exception as uplift_error:
                logger.error(f"Uplift AI TTS failed: {uplift_error}")
                logger.info("Attempting fallback to OpenAI...")
                # Fall through to OpenAI
        
        # If Uplift is enabled but no key, report clearly instead of falling back
        if USE_UPLIFT_TTS and not UPLIFT_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="Uplift TTS is enabled but UPLIFT_API_KEY is missing. Set UPLIFT_API_KEY in server/.env or disable USE_UPLIFT_TTS."
            )

        # Use OpenAI TTS API (default or fallback)
        if not OPENAI_KEY_PRESENT:
            raise HTTPException(
                status_code=503,
                detail="TTS service unavailable. Missing OPENAI_API_KEY in server/.env."
            )

        voice = normalize_openai_voice(request.voice, request.language)

        logger.info(f"Using OpenAI TTS with voice: {voice}")
        try:
            response = openai.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=request.text,
                response_format="mp3"
            )
        except openai.AuthenticationError as auth_err:
            raise HTTPException(status_code=401, detail=f"OpenAI authentication failed: {auth_err}")
        
        audio_content = response.content
        import base64
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        logger.info(f"OpenAI TTS success: {len(audio_content)} bytes")
        return {
            "status": "success",
            "language": request.language,
            "audio_format": "mp3",
            "audio": audio_base64,
            "provider": "openai",
            "message": "Audio generated successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TTS failed: {str(e)}")

@app.post("/api/stt")
async def speech_to_text(request: STTRequest):
    """
    Convert speech to text using OpenAI Whisper
    Supports multiple languages
    """
    try:
        import base64
        import tempfile
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(request.audio_data)
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_audio_path = temp_audio.name
        
        # Transcribe using Whisper
        with open(temp_audio_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=LANGUAGE_CODES.get(request.language, "en")
            )
        
        # Clean up
        os.remove(temp_audio_path)
        
        return {
            "status": "success",
            "text": transcript.text,
            "language": request.language
        }
    
    except Exception as e:
        logger.error(f"STT error: {e}")
        raise HTTPException(status_code=500, detail=f"STT failed: {str(e)}")

@app.post("/api/chat")
async def chat_completion(request: ChatRequest):
    """
    Process chat message with OpenAI and return response with TTS
    """
    try:
        language = request.language
        
        # Build system prompt based on language
        system_prompts = {
            "English": "You are a helpful AI assistant that speaks clearly in English.",
            "Urdu": "آپ ایک مددگار AI اسسٹنٹ ہیں جو اردو میں واضح طور پر بولتے ہیں۔",
            "Sindhi": "توهان هڪ مددگار AI اسسٽنٽ آهيو جيڪو سنڌي ۾ واضح طور تي ڳالهائيندو آهي۔"
        }
        
        system_prompt = system_prompts.get(language, system_prompts["English"])
        
        # Prepare messages
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(request.history)
        messages.append({"role": "user", "content": request.message})
        
        # Get LLM response
        logger.info(f"Chat request in {language}: {request.message[:50]}...")
        
        completion = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        response_text = completion.choices[0].message.content
        
        # Generate TTS for response (prefer Uplift AI for lower latency)
        if USE_UPLIFT_TTS and uplift_client and UPLIFT_API_KEY:
            try:
                if not uplift_client.connected:
                    await uplift_client.connect()
                
                voice_id = UPLIFT_VOICE_MAPPING.get(language, "v_meklc281")
                audio_content = await uplift_client.synthesize_complete(
                    text=response_text,
                    voice_id=voice_id,
                    output_format="MP3_22050_32"
                )
                
                import base64
                audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            except Exception as uplift_error:
                logger.warning(f"Uplift AI TTS failed in chat, using OpenAI: {uplift_error}")
                # Fallback to OpenAI
                if not OPENAI_KEY_PRESENT:
                    raise HTTPException(status_code=503, detail="Chat TTS unavailable. Missing OPENAI_API_KEY.")
                voice = normalize_openai_voice(None, language)
                try:
                    audio_response = openai.audio.speech.create(
                        model="tts-1",
                        voice=voice,
                        input=response_text,
                        response_format="mp3"
                    )
                except openai.AuthenticationError as auth_err:
                    raise HTTPException(status_code=401, detail=f"OpenAI authentication failed: {auth_err}")
                import base64
                audio_base64 = base64.b64encode(audio_response.content).decode('utf-8')
        else:
            # Use OpenAI TTS
            if not OPENAI_KEY_PRESENT:
                raise HTTPException(status_code=503, detail="Chat TTS unavailable. Missing OPENAI_API_KEY.")
            voice = normalize_openai_voice(None, language)
            try:
                audio_response = openai.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=response_text,
                    response_format="mp3"
                )
            except openai.AuthenticationError as auth_err:
                raise HTTPException(status_code=401, detail=f"OpenAI authentication failed: {auth_err}")
            import base64
            audio_base64 = base64.b64encode(audio_response.content).decode('utf-8')
        
        return {
            "status": "success",
            "text": response_text,
            "language": language,
            "audio": audio_base64,
            "audio_format": "mp3"
        }
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.websocket("/ws/realtime")
async def websocket_realtime(websocket: WebSocket):
    """
    WebSocket endpoint for real-time voice interaction
    """
    await websocket.accept()
    logger.info("WebSocket connection established")
    
    try:
        while True:
            # Receive data from client
            data = await websocket.receive_json()
            
            message_type = data.get("type")
            
            if message_type == "audio":
                # Process audio data
                audio_data = data.get("data")
                language = data.get("language", "English")
                
                # Transcribe audio
                stt_request = STTRequest(audio_data=audio_data, language=language)
                stt_result = await speech_to_text(stt_request)
                
                # Get chat response
                chat_request = ChatRequest(
                    message=stt_result["text"],
                    language=language
                )
                chat_result = await chat_completion(chat_request)
                
                # Send response back
                await websocket.send_json({
                    "type": "response",
                    "transcription": stt_result["text"],
                    "response_text": chat_result["text"],
                    "response_audio": chat_result["audio"],
                    "language": language
                })
            
            elif message_type == "text":
                # Process text message
                text = data.get("text")
                language = data.get("language", "English")
                
                chat_request = ChatRequest(message=text, language=language)
                chat_result = await chat_completion(chat_request)
                
                await websocket.send_json({
                    "type": "response",
                    "response_text": chat_result["text"],
                    "response_audio": chat_result["audio"],
                    "language": language
                })
            
            elif message_type == "ping":
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

