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

**Text-to-Speech:**
```bash
curl -X POST http://localhost:8000/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "سنڌي ٻولي خوبصورت آهي.",
    "language": "Sindhi",
    "emotion": "neutral"
  }'
```

**Emotion Analysis:**
```bash
curl -X POST http://localhost:8000/api/emotion/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "text": "مان خوش آهيان.",
    "language": "Sindhi"
  }'
```

## 🧠 Offline TTS Pipeline

Pipeline stages (modular, testable, no network calls):

Text Input → Language Normalization → G2P → Emotion Detection → Prosody Mapping → Phoneme Audio Synthesis → WAV Output

Core modules:
- `server/text_normalizer.py`
- `server/g2p.py`
- `server/emotion_detector.py`
- `server/prosody.py`
- `server/universal_tts.py`
- `server/tts_pipeline.py`

## 🧰 Dataset Preparation Tools

Use offline tools to prepare future training datasets (no training performed yet):

```bash
cd server
python dataset_tools.py --input ./raw_wavs --output ./dataset/audio --trim --slice-ms 8000
```

If you provide matching transcripts in a `--text` folder, metadata will be created:

```
dataset/audio/
  0001.wav
  0002.wav
  metadata.csv
  metadata.json
```

## 🧪 Tests

Run offline test suite:

```bash
cd server
pytest
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
- Verify `server/.env` exists and has offline defaults

### Frontend connection fails
- Ensure backend is running on `http://localhost:8000`
- Check CORS settings in `main.py`
- Verify `NEXT_PUBLIC_API_URL` in `web/.env.local`

### No audio playback
- Check browser autoplay restrictions
- Verify audio format is WAV
- Check browser console for errors

### Language not working correctly
- Check language mappings in `server/universal_tts.py`
- Review `server/text_normalizer.py` for normalization rules

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

