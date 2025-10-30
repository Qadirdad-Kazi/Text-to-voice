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
LIVEKIT_URL = os.getenv("LIVEKIT_URL", "wss://your-livekit-server.com")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
UPLIFT_API_KEY = os.getenv("UPLIFT_API_KEY")
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")
USE_UPLIFT_TTS = os.getenv("USE_UPLIFT_TTS", "false").lower() == "true"

# Configure OpenAI
openai.api_key = OPENAI_API_KEY

# Initialize Uplift AI client if enabled
uplift_client = None
if USE_UPLIFT_TTS and UPLIFT_API_KEY:
    from uplift_client import UpliftWebSocketClient
    uplift_client = UpliftWebSocketClient(UPLIFT_API_KEY)
    logger.info("Uplift AI WebSocket TTS enabled")

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
        "openai_configured": OPENAI_API_KEY and OPENAI_API_KEY != "sk-placeholder"
    }

@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "backend": "online",
        "uplift_ai": {
            "enabled": USE_UPLIFT_TTS,
            "client_initialized": uplift_client is not None,
            "connected": uplift_client.connected if uplift_client else False
        },
        "openai": {
            "configured": bool(OPENAI_API_KEY and OPENAI_API_KEY != "sk-placeholder")
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
                        'https://api.upliftai.org/v1/synthesis/text-to-speech',
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
        
        # Use OpenAI TTS API (default or fallback)
        if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-placeholder":
            raise HTTPException(
                status_code=503,
                detail="TTS service unavailable. Please configure OPENAI_API_KEY or fix Uplift AI configuration."
            )
        
        voice = request.voice or VOICE_MAPPING.get(request.language, "alloy")
        
        logger.info(f"Using OpenAI TTS with voice: {voice}")
        response = openai.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=request.text,
            response_format="mp3"
        )
        
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
                voice = VOICE_MAPPING.get(language, "alloy")
                audio_response = openai.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=response_text,
                    response_format="mp3"
                )
                import base64
                audio_base64 = base64.b64encode(audio_response.content).decode('utf-8')
        else:
            # Use OpenAI TTS
            voice = VOICE_MAPPING.get(language, "alloy")
            audio_response = openai.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=response_text,
                response_format="mp3"
            )
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

@app.post("/api/settings/update-keys")
async def update_api_keys(
    uplift_api_key: Optional[str] = None,
    openai_api_key: Optional[str] = None
):
    """Update API keys in the .env file"""
    try:
        env_path = os.path.join(os.path.dirname(__file__), '.env')
        
        # Read existing .env file
        env_vars = {}
        if os.path.exists(env_path):
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()
        
        # Update keys if provided
        updated = []
        if uplift_api_key:
            env_vars['UPLIFT_API_KEY'] = uplift_api_key
            updated.append('Uplift AI')
            # Update global variable
            global UPLIFT_API_KEY
            UPLIFT_API_KEY = uplift_api_key
            
        if openai_api_key:
            env_vars['OPENAI_API_KEY'] = openai_api_key
            updated.append('OpenAI')
            # Update global variable
            global OPENAI_API_KEY
            OPENAI_API_KEY = openai_api_key
            # Update OpenAI client
            openai.api_key = openai_api_key
        
        # Write back to .env file
        with open(env_path, 'w', encoding='utf-8') as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        return {
            "status": "success",
            "message": f"Updated {', '.join(updated)} API key(s)",
            "updated": updated
        }
    
    except Exception as e:
        logger.error(f"Failed to update API keys: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update API keys: {str(e)}")

@app.get("/api/settings/current")
async def get_current_settings():
    """Get current API key status (masked for security)"""
    try:
        def mask_key(key: Optional[str]) -> str:
            if not key or key == "placeholder":
                return "Not set"
            if len(key) < 10:
                return "Invalid"
            return f"{key[:8]}...{key[-4:]}"
        
        return {
            "uplift_api_key": mask_key(UPLIFT_API_KEY),
            "openai_api_key": mask_key(OPENAI_API_KEY),
            "uplift_enabled": USE_UPLIFT_TTS,
            "uplift_active": bool(UPLIFT_API_KEY and UPLIFT_API_KEY != "placeholder"),
            "openai_active": bool(OPENAI_API_KEY and OPENAI_API_KEY != "placeholder" and OPENAI_API_KEY.startswith("sk-"))
        }
    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get settings: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

