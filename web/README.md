# Web (Next.js) — Offline Voice Agent UI

This `web/` folder contains the Next.js client for the offline phoneme TTS backend.

## Setup

1. Install dependencies:
```bash
cd web
npm install
```

2. Create `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Running

```bash
# Development
npm run dev

# Production build
npm run build
npm start
```

## Features

- Offline TTS requests to `/api/tts`
- Rule-based emotion analysis via `/api/emotion/analyze`
- Language selection (English, Urdu, Sindhi)
- Prosody controls (pitch and rate)
- Audio playback with waveform visualization

## Tech Stack

- Next.js 14
- React 18
- Tailwind CSS
- TypeScript

## Development

The app will be available at http://localhost:3000

Make sure the backend is running at http://localhost:8000

