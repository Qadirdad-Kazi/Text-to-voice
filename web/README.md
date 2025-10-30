# Web (Next.js) — Uplift TTS Demo

This `web/` folder contains a simplified Next.js client that demonstrates calling Uplift's TTS API directly from the browser.

Important: Using `NEXT_PUBLIC_UPLIFT_API_KEY` in the browser exposes it publicly. This setup is only appropriate for local testing. For production, use a server-side proxy.

Setup

1. Install dependencies

```powershell
cd web
npm install
```

2. Provide your Uplift API key

Create `web/.env.local` and add:

```
NEXT_PUBLIC_UPLIFT_API_KEY=your_uplift_api_key_here
```

3. Run the dev server

```powershell
npm run dev
```

Open `http://localhost:3000`.

Notes
- The current `VoiceAgent` component (in `web/components/VoiceAgent.tsx`) performs a POST to `https://api.upliftai.org/v1/tts` and expects a binary MP3 response. Adjust the endpoint and payload if the official docs differ.
- If you want a secure integration, I can add a minimal server proxy that keeps the API key secret.
# Frontend - LiveKit Voice Agent

Next.js frontend for the LiveKit Voice Agent.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_LIVEKIT_URL=wss://your-project.livekit.cloud
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

- Real-time voice interaction
- Text chat interface
- Language selection (English, Urdu, Sindhi)
- Voice visualizer
- Responsive design

## Tech Stack

- Next.js 14
- React 18
- LiveKit Client SDK
- Tailwind CSS
- TypeScript

## Development

The app will be available at http://localhost:3000

Make sure the backend is running at http://localhost:8000

