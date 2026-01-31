# Quick Start: Emotion-Aware Sindhi TTS

## Installation

```bash
# 1. Install backend dependencies
cd server
pip install -r requirements.txt

# 2. Install FFmpeg (required for audio processing)
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg

# 3. Install frontend dependencies
cd ../web
npm install
```

## Configuration

Create `server/.env`:
```env
OPENAI_API_KEY=sk-your-key-here
LIVEKIT_API_KEY=your-livekit-key
LIVEKIT_API_SECRET=your-livekit-secret
LIVEKIT_URL=wss://your-project.livekit.cloud
DEFAULT_LANGUAGE=sd
```

## Running

```bash
# Terminal 1 - Backend
cd server
python main.py

# Terminal 2 - Frontend
cd web
npm run dev
```

Visit: http://localhost:3000

## Features

### 🎭 Emotion Detection
- **Auto-Detect**: Analyzes text for emotions
- **Manual Override**: Select specific emotion
- Supports: Happy, Sad, Angry, Calm, Excited, Neutral

### 🎤 Custom Sindhi TTS
- Self-hosted, no external API needed
- Natural Sindhi pronunciation
- Emotion-aware prosody adjustments

### 🌍 Multi-Language
- English: OpenAI TTS
- Urdu (اردو): OpenAI/Uplift AI TTS
- Sindhi (سنڌي): Custom TTS Engine

## Usage Examples

### Example 1: Auto-Detect Emotion
```javascript
// Send request to /api/tts
{
  "text": "مون کي تمام گهڻي خوشي ٿي آهي",
  "language": "Sindhi",
  "emotion": "auto"  // Auto-detect
}

// Response includes detected emotion
{
  "emotion": "happy",
  "emotion_confidence": 0.87,
  "audio": "base64_audio..."
}
```

### Example 2: Manual Emotion
```javascript
{
  "text": "اسان هي ڪم ڪري سگهون ٿا",
  "language": "Sindhi",
  "emotion": "calm"  // Force calm emotion
}
```

### Example 3: Emotion Analysis Only
```javascript
// POST /api/emotion/analyze
{
  "text": "ڇا توهان مون کي مدد ڪري سگهو ٿا؟",
  "language": "Sindhi"
}

// Get detailed emotion breakdown
{
  "primary_emotion": "neutral",
  "confidence": 0.65,
  "emotion_scores": {
    "neutral": 0.65,
    "curious": 0.25,
    "polite": 0.10
  }
}
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tts` | POST | Text-to-Speech with emotion |
| `/api/emotion/analyze` | POST | Analyze text emotion |
| `/api/health` | GET | System status |
| `/api/chat` | POST | Chat with emotion-aware TTS |

## Frontend Controls

1. **🌍 Language**: Select Sindhi/Urdu/English
2. **🎭 Emotion**: Auto-detect or manual
3. **🎤 Voice**: Voice style (non-Sindhi)
4. **⚡ Speed**: Playback rate (0.5x - 1.5x)

## Testing

### Test Sindhi TTS
```bash
curl -X POST http://localhost:8000/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "سلام",
    "language": "Sindhi",
    "emotion": "auto"
  }'
```

### Test Emotion Detection
```bash
curl -X POST http://localhost:8000/api/emotion/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "مون کي خوشي آهي",
    "language": "Sindhi"
  }'
```

### Check Health
```bash
curl http://localhost:8000/api/health
```

## Emotion Mapping

| Emotion | Speaking Rate | Pitch | Use Case |
|---------|--------------|-------|----------|
| **Happy** 😊 | +15% | +20% | Positive news, celebrations |
| **Sad** 😢 | -15% | -10% | Condolences, disappointments |
| **Angry** 😠 | +20% | +15% | Protests, strong opinions |
| **Calm** 😌 | -10% | -5% | Meditation, relaxation |
| **Excited** 🤩 | +25% | +30% | Sports, announcements |
| **Neutral** 😐 | Normal | Normal | News, documentation |

## Troubleshooting

### Backend won't start
```bash
# Check Python version (3.9+)
python --version

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### "FFmpeg not found"
```bash
# Test FFmpeg
ffmpeg -version

# Install if missing
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt install ffmpeg
```

### "Custom Sindhi TTS not available"
```bash
# Check logs
python main.py

# Should see:
# "Custom Sindhi TTS engine initialized"
```

### Audio quality issues
- Current engine is phoneme-based (demo)
- For production: Use neural TTS models
- See EMOTION_TTS_GUIDE.md for neural integration

## Next Steps

1. ✅ Test with sample Sindhi text
2. ✅ Try different emotions
3. ✅ Experiment with prosody settings
4. 📖 Read full guide: EMOTION_TTS_GUIDE.md
5. 🚀 Deploy to production

## Performance Tips

- Cache emotion analysis for repeated text
- Use batch processing for multiple paragraphs
- Enable Uplift AI for faster Urdu TTS
- Consider GPU acceleration for neural models

## Development

### Add New Emotion
Edit `server/emotion_detector.py`:
```python
self.emotion_keywords = {
    'grateful': {
        'sd': ['شڪريو', 'مهرباني'],
        # Add more keywords
    }
}
```

### Adjust Prosody
Edit `server/sindhi_tts.py`:
```python
def _get_emotion_prosody(self, emotion: str):
    prosody_params = {
        'grateful': {
            'rate_modifier': 0.95,
            'pitch_modifier': 1.05,
            # Adjust parameters
        }
    }
```

### Add Neural Model
```python
from sindhi_tts import SindhiTTSEnhanced

engine = SindhiTTSEnhanced(
    use_neural=True,
    model_path="models/sindhi_tts.pth"
)
```

## Resources

- Full Documentation: `EMOTION_TTS_GUIDE.md`
- Main README: `README.md`
- API Reference: See documentation above
- Examples: `/examples` directory (if available)

## Support

Check system status:
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "backend": "online",
  "custom_features": {
    "sindhi_tts": true,
    "emotion_detection": true
  }
}
```

---

**Happy Synthesizing! 🎙️🎭**
