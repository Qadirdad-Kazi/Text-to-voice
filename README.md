# 🎙️ Offline Sindhi Phoneme TTS - Multi-Language Voice Agent

A fully offline, self-hosted phoneme-based TTS system with emotion control for English, Urdu (اردو), and Sindhi (سنڌي). No external APIs or cloud services are used.

## 🌟 Features

- **Fully Offline**: No cloud or API dependencies
- **Multi-Language Support**: English, Urdu (اردو), and Sindhi (سنڌي)
- **Phoneme TTS Engine**: Offline, emotion-aware synthesis
- **Rule-Based Emotion Detection**: No ML required
- **Prosody Control**: Pitch, speed, pauses, and emotion mapping
- **Dataset Tooling Ready**: Audio slicing, silence trimming, metadata generation
- **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS

## 📋 Prerequisites

Before you begin, ensure you have:

- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)
- No external API keys required

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd TextToVoice
```

### 2. Backend Setup

```bash
cd server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
# or
cp .env.example .env    # macOS/Linux
```

**Edit `server/.env` for offline settings:**

```env
DEFAULT_LANGUAGE=en
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
DATASET_SAMPLE_RATE=16000
DATASET_CHANNELS=1
```

**Start the backend:**

```bash
# Start FastAPI server
python main.py

# Or use uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

Open a new terminal:

```bash
cd web

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Start the development server
npm run dev
```

The web app will be available at `http://localhost:3000`

### 4. Start Using the Voice Agent

1. Open your browser to `http://localhost:3000`
2. Select your preferred language (English, Urdu, or Sindhi)
3. Type text and synthesize speech

## 🗂️ Project Structure

```
TextToVoice/
├── server/                 # Python FastAPI backend
│   ├── main.py            # FastAPI server with REST endpoints
│   ├── tts_pipeline.py    # Offline TTS pipeline
│   ├── universal_tts.py   # Phoneme synthesis engine
│   ├── text_normalizer.py # Language normalization
│   ├── g2p.py             # Grapheme-to-phoneme mapping
│   ├── prosody.py         # Prosody mapping
│   ├── dataset_tools.py   # Dataset preparation tools
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Environment variables template
│
├── web/                   # Next.js frontend
│   ├── app/              # Next.js app directory
│   │   ├── page.tsx      # Home page
│   │   ├── layout.tsx    # Root layout
│   │   └── globals.css   # Global styles
│   ├── components/       # React components
│   │   └── VoiceAgent.tsx # Main voice agent component
│   ├── package.json      # Node dependencies
│   ├── tsconfig.json     # TypeScript config
│   └── tailwind.config.js # Tailwind CSS config
│
└── README.md             # This file
```

## 🔧 API Endpoints

### Backend (`http://localhost:8000`)

- `GET /` - Health check
- `POST /api/tts` - Text-to-speech conversion (offline phoneme TTS)
- `POST /api/emotion/analyze` - Rule-based emotion analysis

### Example API Usage

**Generate Token:**
```bash
curl -X POST http://localhost:8000/api/token \
  -H "Content-Type: application/json" \
  -d '{
    "room_name": "test-room",
    "participant_name": "User1",
    "language": "English"
  }'
```

**Chat Request:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, how are you?",
    "language": "English"
  }'
```

## 🌍 Language Configuration

The system supports three languages with the following mappings:

| Language | Code |
|----------|------|
| English  | en   |
| Urdu     | ur   |
| Sindhi   | sd   |

Phoneme mappings are defined in `server/universal_tts.py`.

## 🎨 Customization

### Change System Prompts

Edit phoneme mappings and prosody in `server/universal_tts.py` and `server/emotion_detector.py`.

### Modify UI Theme

Edit `web/tailwind.config.js` to change colors:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#3b82f6',  // Change this to your color
      },
    },
  },
}
```

## 🚀 Deployment

### Backend Deployment

**Option 1: Render**
1. Push code to GitHub
2. Create new Web Service on Render
3. Set environment variables
4. Deploy!

**Option 2: Railway**
```bash
railway init
railway up
```

**Option 3: AWS Lambda**
Use AWS SAM or Serverless Framework

### Frontend Deployment

**Vercel (Recommended):**
```bash
cd web
vercel
```

**Netlify:**
```bash
cd web
netlify deploy
```

## 🐛 Troubleshooting

### Backend won't start
- Check if Python 3.9+ is installed: `python --version`
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Verify `.env` file has correct API keys

### Frontend connection fails
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in `main.py`
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

### No audio playback
- Check browser permissions for microphone
- Verify LiveKit URL is correct
- Check browser console for errors

### Language not working correctly
- Ensure OpenAI API key has access to Whisper and TTS
- Check language code mappings in `main.py`
- Verify audio format is supported

## 📚 Learn More

- [LiveKit Documentation](https://docs.livekit.io/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [Uplift AI WebSocket TTS](https://docs.upliftai.org/tutorials/websocket-conversational-ai) - For ~300ms latency
- [Uplift AI LiveKit Guide](https://docs.upliftai.org/tutorials/livekit-voice-agent)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### 🚀 Uplift AI Integration

For even lower latency (~300ms first chunk), enable Uplift AI WebSocket TTS:
# Web-only Text-to-Speech (Uplift) Demo

This repository has been trimmed to include only the Next.js web client. The previous backend and LiveKit integration were removed per request. The web app now demonstrates a client-side TTS flow using the Uplift TTS API.

Important notes:
- This is a client-only demo intended for local testing. Putting an API key into `NEXT_PUBLIC_*` exposes it to end users and is not secure for production.

Quick start (web only):

1. Install dependencies

```powershell
cd web
npm install
```

2. Add your Uplift API key to `.env.local` (browser-visible):

```powershell
# In the repository root
setx NEXT_PUBLIC_UPLIFT_API_KEY "your_uplift_api_key"
# Or create web/.env.local with:
# NEXT_PUBLIC_UPLIFT_API_KEY=your_uplift_api_key
```

3. Run the dev server

```powershell
cd web
npm run dev
```

4. Open http://localhost:3000 and use the UI to type text and synthesize audio via Uplift.

If you need a secure server-side integration to keep your Uplift API key secret, I can add a small proxy server — let me know.

