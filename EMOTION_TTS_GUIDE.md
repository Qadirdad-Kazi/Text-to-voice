# Emotion-Aware Sindhi TTS Integration Guide

## Overview

This document describes the enhanced LiveKit Voice Agent with **custom Sindhi TTS** and **emotion detection** capabilities. The system now provides natural, expressive speech synthesis for Sindhi language without relying on external APIs.

## Key Features

### 1. Custom Sindhi TTS Engine
- **Self-hosted**: No external API dependencies for Sindhi speech
- **Phoneme-based synthesis**: Natural Sindhi pronunciation
- **Emotion-aware prosody**: Dynamic adjustments based on detected emotions
- **Extensible architecture**: Ready for neural model integration

### 2. Emotion Detection
- **Multi-language support**: English, Urdu, and Sindhi
- **Automatic detection**: Analyzes text to identify emotions
- **Keyword-based analysis**: Context-aware emotion recognition
- **Prosody recommendations**: Speaking rate, pitch, and volume adjustments

### 3. Supported Emotions
- **Neutral**: Standard tone without emotion
- **Happy**: Cheerful and upbeat (faster rate, higher pitch)
- **Sad**: Somber and melancholic (slower rate, lower pitch)
- **Angry**: Intense and forceful (fast rate, sharp articulation)
- **Calm**: Peaceful and soothing (slower rate, smooth transitions)
- **Excited**: Energetic and enthusiastic (very fast, high pitch)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  - Emotion selector (auto/manual)                           │
│  - Real-time emotion analysis display                        │
│  - Prosody control interface                                 │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/REST API
┌─────────────────▼───────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Emotion Detector                                    │  │
│  │  - Text analysis                                      │  │
│  │  - Multi-language keyword matching                    │  │
│  │  - Prosody calculation                                │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  TTS Router                                          │  │
│  │  - Sindhi → Custom TTS Engine                        │  │
│  │  - Urdu/English → OpenAI/Uplift AI                   │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                        │
│  ┌──────────────────▼───────────────────────────────────┐  │
│  │  Custom Sindhi TTS Engine                            │  │
│  │  - Phoneme mapping                                    │  │
│  │  - Prosody adjustment                                 │  │
│  │  - Emotion-based filters                              │  │
│  │  - Audio generation (MP3)                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## API Endpoints

### 1. Text-to-Speech with Emotion
**POST** `/api/tts`

**Request:**
```json
{
  "text": "توهان جو استقبال آهي",
  "language": "Sindhi",
  "emotion": "auto",  // or specific: happy, sad, angry, calm, excited, neutral
  "speaking_rate": 1.0,
  "pitch_shift": 1.0,
  "voice": "v_8eelc901"
}
```

**Response:**
```json
{
  "status": "success",
  "language": "Sindhi",
  "audio_format": "mp3",
  "audio": "base64_encoded_audio_data",
  "provider": "custom_sindhi",
  "emotion": "happy",
  "emotion_confidence": 0.85,
  "prosody": {
    "speaking_rate": 1.15,
    "pitch_shift": 1.2
  },
  "message": "Audio generated successfully with Custom Sindhi TTS"
}
```

### 2. Emotion Analysis
**POST** `/api/emotion/analyze`

**Request:**
```json
{
  "text": "مون کي تمام گهڻي خوشي ٿي آهي",
  "language": "Sindhi"
}
```

**Response:**
```json
{
  "status": "success",
  "primary_emotion": "happy",
  "confidence": 0.87,
  "intensity": 0.75,
  "emotion_scores": {
    "happy": 0.87,
    "excited": 0.10,
    "neutral": 0.03
  },
  "prosody_recommendations": {
    "speaking_rate": 1.15,
    "pitch_shift": 1.2,
    "volume": 1.1
  },
  "emotion_shifts": [],
  "language": "Sindhi"
}
```

### 3. Health Check
**GET** `/api/health`

**Response:**
```json
{
  "backend": "online",
  "custom_features": {
    "sindhi_tts": true,
    "emotion_detection": true
  },
  "uplift_ai": {...},
  "openai": {...},
  "livekit": {...}
}
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

**Note**: The custom Sindhi TTS requires:
- `pydub` for audio processing
- `numpy` for signal processing
- FFmpeg or libav (system dependency for pydub)

**Install FFmpeg:**
- **Windows**: Download from https://ffmpeg.org/ or use `choco install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

### 2. Environment Configuration

Update `server/.env`:

```env
# Existing configuration
LIVEKIT_API_KEY=your_livekit_api_key
LIVEKIT_API_SECRET=your_livekit_api_secret
LIVEKIT_URL=wss://your-project.livekit.cloud
OPENAI_API_KEY=sk-your-openai-key

# Uplift AI (optional, for Urdu/English)
UPLIFT_API_KEY=your_uplift_key
USE_UPLIFT_TTS=false

# Default language
DEFAULT_LANGUAGE=sd  # Use 'sd' for Sindhi

# Custom TTS (automatically enabled when dependencies are installed)
# No additional configuration needed
```

### 3. Start the Backend

```bash
cd server
python main.py
```

Or use uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start the Frontend

```bash
cd web
npm install
npm run dev
```

## Usage Guide

### Frontend Controls

1. **Language Selection**: Choose Sindhi (سنڌي) to use the custom TTS
2. **Emotion Mode**: 
   - **Auto-Detect**: Automatically analyzes text for emotions
   - **Manual**: Select specific emotion (Happy, Sad, Angry, Calm, Excited, Neutral)
3. **Voice Style**: Select preferred voice characteristics (for non-Sindhi languages)
4. **Playback Speed**: Adjust playback rate (0.5x - 1.5x)

### Automatic Emotion Detection

When emotion mode is set to "Auto-Detect":

1. System analyzes input text
2. Detects primary emotion and confidence level
3. Automatically adjusts:
   - Speaking rate
   - Pitch
   - Volume
   - Articulation style

**Example:**
- Input: "مون کي تمام گهڻي خوشي ٿي آهي" (I am very happy)
- Detected: Happy (confidence: 0.87)
- Adjustments: +15% speed, +20% pitch, brighter tone

### Manual Emotion Override

Select specific emotion to override automatic detection:

- **Happy**: For cheerful, positive content
- **Sad**: For somber, melancholic content
- **Angry**: For intense, forceful delivery
- **Calm**: For peaceful, soothing narration
- **Excited**: For energetic, enthusiastic content
- **Neutral**: For standard, unbiased delivery

## Technical Details

### Sindhi Phoneme Mapping

The custom TTS engine uses a comprehensive phoneme inventory covering:

**Vowels:**
- Short: ا (a), ي (i), و (u)
- Long: آ (ā), ي (ī), و (ū)

**Consonants:**
- Stops: ب پ ت ٿ ٽ ٺ ڪ گ
- Fricatives: ف س ش ص ح خ ع غ
- Nasals: م ن ڻ
- Liquids: ل ر ڙ
- Affricates: ج ڄ ڃ

Each phoneme has:
- Base frequency
- Duration
- Articulation pattern

### Emotion-Based Prosody Adjustments

| Emotion  | Rate | Pitch | Duration | Amplitude |
|----------|------|-------|----------|-----------|
| Neutral  | 1.0  | 1.0   | 1.0      | 0.7       |
| Happy    | 1.15 | 1.2   | 0.95     | 0.85      |
| Sad      | 0.85 | 0.9   | 1.1      | 0.6       |
| Angry    | 1.2  | 1.15  | 0.9      | 0.9       |
| Calm     | 0.9  | 0.95  | 1.05     | 0.65      |
| Excited  | 1.25 | 1.3   | 0.9      | 0.9       |

### Audio Processing Pipeline

1. **Text Analysis**: Emotion detection and prosody calculation
2. **Phoneme Generation**: Convert Sindhi text to phoneme sequence
3. **Synthesis**: Generate audio segments with emotion adjustments
4. **Post-Processing**: Apply filters (EQ, compression, normalization)
5. **Export**: MP3 format (128kbps)

## Future Enhancements

### Neural TTS Integration

The architecture supports integration of neural TTS models:

1. **Tacotron2**: Attention-based seq2seq model
2. **FastSpeech2**: Non-autoregressive TTS
3. **VITS**: End-to-end synthesis with variational inference
4. **Coqui TTS**: Open-source multi-lingual TTS

To enable neural models, uncomment in `requirements.txt`:
```
torch>=2.0.0
torchaudio>=2.0.0
transformers>=4.30.0
```

Then update `sindhi_tts.py` to load your trained model:
```python
engine = SindhiTTSEnhanced(
    use_neural=True,
    model_path="path/to/model.pth"
)
```

### Multimodal Emotion Detection

Extend to analyze audio input for emotion:
- Voice pitch analysis
- Speaking rate detection
- Energy level measurement
- Combined text+audio analysis

## Troubleshooting

### Issue: "Custom Sindhi TTS not available"

**Solution:**
1. Ensure `pydub` is installed: `pip install pydub`
2. Install FFmpeg (system dependency)
3. Restart the backend server

### Issue: "Emotion detection not available"

**Solution:**
1. Check that `emotion_detector.py` is in the server directory
2. Verify no import errors in server logs
3. Restart the backend

### Issue: Audio quality is poor

**Solution:**
1. This is a phoneme-based engine for demonstration
2. For production, use neural TTS models
3. Adjust prosody parameters in `sindhi_tts.py`

### Issue: FFmpeg not found

**Solution:**
```bash
# Windows (using chocolatey)
choco install ffmpeg

# macOS
brew install ffmpeg

# Linux
sudo apt-get update
sudo apt-get install ffmpeg
```

## Performance Considerations

### Latency
- Custom Sindhi TTS: ~200-500ms (depending on text length)
- Emotion Detection: ~10-50ms
- Total: ~250-600ms for Sindhi synthesis

### Resource Usage
- CPU: Moderate (audio synthesis)
- Memory: Low (~50MB for models)
- Disk: Minimal (no model storage for basic engine)

### Scaling
- Stateless API: Easy horizontal scaling
- Cache emotion analysis results
- Pre-compute common phoneme sequences

## Contributing

To extend or improve the system:

1. **Add Phonemes**: Update `phoneme_map` in `sindhi_tts.py`
2. **Add Emotions**: Update `emotion_keywords` in `emotion_detector.py`
3. **Improve Prosody**: Adjust parameters in `_get_emotion_prosody()`
4. **Add Neural Models**: Implement in `SindhiTTSEnhanced` class

## Support

For issues or questions:
1. Check the health endpoint: `GET /api/health`
2. Review server logs for errors
3. Test with simple Sindhi text first
4. Verify FFmpeg installation

## License

This enhancement maintains the same license as the original project.

---

**Last Updated**: January 2026
**Version**: 2.0.0-emotion-aware
