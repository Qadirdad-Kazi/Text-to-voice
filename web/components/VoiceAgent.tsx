'use client'

import { useState, useEffect, useRef } from 'react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: Date
  audioUrl?: string
  audioBlob?: Blob
  provider?: string
}

export default function VoiceAgent() {
  const [language, setLanguage] = useState<string>('English')
  const [selectedVoice, setSelectedVoice] = useState<string>('v_8eelc901')
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1.0)
  const [messages, setMessages] = useState<Message[]>([])
  const [textInput, setTextInput] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentlyPlaying, setCurrentlyPlaying] = useState<number | null>(null)
  const [darkMode, setDarkMode] = useState(false)
  const [realtimePreview, setRealtimePreview] = useState(false)
  const [isGeneratingPreview, setIsGeneratingPreview] = useState(false)
  const [multiLanguageMode, setMultiLanguageMode] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [upliftApiKey, setUpliftApiKey] = useState('')
  const [openaiApiKey, setOpenaiApiKey] = useState('')
  const [currentSettings, setCurrentSettings] = useState<any>(null)
  const [isSavingSettings, setIsSavingSettings] = useState(false)

  const messagesEndRef = useRef<HTMLDivElement>(null)
  const audioRefs = useRef<{ [key: number]: HTMLAudioElement }>({})
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null)
  const canvasRefs = useRef<{ [key: number]: HTMLCanvasElement }>({})

  // Load dark mode preference from localStorage
  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true'
    setDarkMode(savedDarkMode)
  }, [])

  // Save dark mode preference and apply to document
  useEffect(() => {
    localStorage.setItem('darkMode', darkMode.toString())
    if (darkMode) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, [darkMode])

  // Load current settings when settings modal opens
  useEffect(() => {
    if (showSettings) {
      loadCurrentSettings()
    }
  }, [showSettings])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Load current API key status
  const loadCurrentSettings = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/settings/current')
      const data = await response.json()
      setCurrentSettings(data)
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
  }

  // Save API keys
  const saveApiKeys = async () => {
    if (!upliftApiKey && !openaiApiKey) {
      alert('Please enter at least one API key')
      return
    }

    setIsSavingSettings(true)
    try {
      const params = new URLSearchParams()
      if (upliftApiKey) params.append('uplift_api_key', upliftApiKey)
      if (openaiApiKey) params.append('openai_api_key', openaiApiKey)

      const response = await fetch(`http://localhost:8000/api/settings/update-keys?${params}`, {
        method: 'POST',
      })

      if (!response.ok) {
        throw new Error(`Failed to update keys: ${response.status}`)
      }

      const result = await response.json()
      alert(`✅ ${result.message}`)
      
      // Clear input fields and reload settings
      setUpliftApiKey('')
      setOpenaiApiKey('')
      await loadCurrentSettings()
    } catch (error: any) {
      console.error('Settings update error:', error)
      alert(`❌ Failed to update API keys: ${error.message}`)
    } finally {
      setIsSavingSettings(false)
    }
  }

  // Available Uplift AI voices
  const availableVoices = [
    { id: 'v_8eelc901', name: '🎓 Info/Education', description: 'Clear and easy to understand - Best for articles and tutorials' },
    { id: 'v_30s70t3a', name: '📰 Nostalgic News', description: 'Classic Pakistani news voice - Professional and calm' },
    { id: 'v_yypgzenx', name: '📖 Dada Jee', description: 'Deep storytelling voice - Suspenseful and engaging' },
    { id: 'v_kwmp7zxt', name: '⚡ Gen Z', description: 'Fast and clean - Modern and energetic (Beta)' }
  ]

  // Playback speed options
  const speedOptions = [
    { value: 0.5, label: '0.5x - Very Slow', icon: '🐌' },
    { value: 0.75, label: '0.75x - Slow', icon: '🐢' },
    { value: 1.0, label: '1.0x - Normal', icon: '▶️' },
    { value: 1.25, label: '1.25x - Fast', icon: '⚡' },
    { value: 1.5, label: '1.5x - Very Fast', icon: '🚀' }
  ]

  // Detect language of text using Unicode ranges
  const detectLanguage = (text: string): string => {
    const urduRegex = /[\u0600-\u06FF]/  // Arabic/Urdu Unicode range
    const sindhiRegex = /[\u0600-\u06FF]/  // Sindhi uses similar range
    
    // Count characters in each language
    const urduMatches = text.match(urduRegex)
    const urduCount = urduMatches ? urduMatches.length : 0
    const totalChars = text.replace(/\s/g, '').length
    
    // If more than 30% is Urdu/Sindhi script, detect as Urdu
    if (urduCount / totalChars > 0.3) {
      return 'Urdu'  // Could be enhanced to distinguish Sindhi
    }
    
    return 'English'
  }

  // Split text into language segments
  const splitIntoLanguageSegments = (text: string): Array<{ text: string, language: string }> => {
    // Split by sentences (., !, ?, or newlines)
    const sentences = text.split(/([.!?\n]+)/).filter(s => s.trim())
    const segments: Array<{ text: string, language: string }> = []
    
    let currentText = ''
    let currentLang = ''
    
    sentences.forEach(sentence => {
      const detectedLang = detectLanguage(sentence)
      
      if (currentLang === '' || currentLang === detectedLang) {
        // Same language, accumulate
        currentText += sentence
        currentLang = detectedLang
      } else {
        // Language changed, save previous segment
        if (currentText.trim()) {
          segments.push({ text: currentText.trim(), language: currentLang })
        }
        currentText = sentence
        currentLang = detectedLang
      }
    })
    
    // Add final segment
    if (currentText.trim()) {
      segments.push({ text: currentText.trim(), language: currentLang })
    }
    
    return segments
  }

  const synthesizeAudio = async (text: string, lang: string): Promise<{ blob: Blob, url: string, provider: string } | null> => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    
    try {
      const resp = await fetch(`${API_URL}/api/tts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          text: text, 
          language: lang,
          voice: selectedVoice
        })
      })

      if (!resp.ok) {
        const errorData = await resp.json().catch(() => ({ detail: 'Unknown error' }))
        throw new Error(`TTS request failed: ${resp.status} - ${errorData.detail || 'Unknown error'}`)
      }

      const data = await resp.json()
      
      if (data.audio) {
        const audioBytes = atob(data.audio)
        const arrayBuffer = new ArrayBuffer(audioBytes.length)
        const uint8Array = new Uint8Array(arrayBuffer)
        for (let i = 0; i < audioBytes.length; i++) {
          uint8Array[i] = audioBytes.charCodeAt(i)
        }
        
        const blob = new Blob([arrayBuffer], { type: 'audio/mpeg' })
        const url = URL.createObjectURL(blob)
        
        console.log(`TTS success using ${data.provider}: ${text.substring(0, 50)}...`)
        return { blob, url, provider: data.provider }
      } else {
        throw new Error('No audio data received from server')
      }
    } catch (err: any) {
      console.error('TTS error', err)
      alert(`TTS failed: ${err.message}\n\nMake sure the backend is running at ${API_URL}`)
      return null
    }
  }

  const playAudio = (index: number) => {
    const audio = audioRefs.current[index]
    if (audio) {
      if (currentlyPlaying === index) {
        audio.pause()
        setCurrentlyPlaying(null)
      } else {
        Object.values(audioRefs.current).forEach(a => a.pause())
        audio.playbackRate = playbackSpeed  // Apply playback speed
        audio.play()
        setCurrentlyPlaying(index)
        
        // Animate waveform while playing
        animateWaveform(index, audio)
      }
    }
  }

  // Generate and draw waveform visualization
  const drawWaveform = async (audioBlob: Blob, canvas: HTMLCanvasElement) => {
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
      const arrayBuffer = await audioBlob.arrayBuffer()
      const audioBuffer = await audioContext.decodeAudioData(arrayBuffer)
      
      const data = audioBuffer.getChannelData(0)
      const step = Math.ceil(data.length / canvas.width)
      const amp = canvas.height / 2
      
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      ctx.fillStyle = darkMode ? '#4B5563' : '#E5E7EB'
      
      for (let i = 0; i < canvas.width; i++) {
        let min = 1.0
        let max = -1.0
        
        for (let j = 0; j < step; j++) {
          const datum = data[(i * step) + j]
          if (datum < min) min = datum
          if (datum > max) max = datum
        }
        
        const x = i
        const y = (1 + min) * amp
        const height = Math.max(1, (max - min) * amp)
        
        ctx.fillRect(x, y, 1, height)
      }
    } catch (err) {
      console.error('Waveform generation failed:', err)
    }
  }

  // Animate waveform during playback
  const animateWaveform = (index: number, audio: HTMLAudioElement) => {
    const canvas = canvasRefs.current[index]
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const animate = () => {
      if (audio.paused || audio.ended) return

      const progress = audio.currentTime / audio.duration
      const progressX = Math.floor(progress * canvas.width)

      // Redraw waveform with progress indicator
      ctx.clearRect(0, 0, canvas.width, canvas.height)
      
      // Background waveform (gray)
      ctx.fillStyle = darkMode ? '#4B5563' : '#E5E7EB'
      ctx.fillRect(0, 0, canvas.width, canvas.height)
      
      // Active waveform (blue gradient)
      const gradient = ctx.createLinearGradient(0, 0, progressX, 0)
      gradient.addColorStop(0, '#3B82F6')
      gradient.addColorStop(1, '#8B5CF6')
      ctx.fillStyle = gradient
      ctx.fillRect(0, 0, progressX, canvas.height)

      requestAnimationFrame(animate)
    }

    animate()
  }

  // Update playback speed for all audio elements when changed
  useEffect(() => {
    Object.values(audioRefs.current).forEach(audio => {
      if (audio) {
        audio.playbackRate = playbackSpeed
      }
    })
  }, [playbackSpeed])

  // Real-time preview with debouncing
  useEffect(() => {
    if (!realtimePreview || !textInput.trim() || isLoading) {
      return
    }

    // Clear existing timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }

    // Set new timer (wait 2 seconds after user stops typing)
    debounceTimerRef.current = setTimeout(async () => {
      const previewText = textInput.trim()
      
      // Only generate if text is substantial (at least 5 characters)
      if (previewText.length >= 5) {
        setIsGeneratingPreview(true)
        try {
          const audioResult = await synthesizeAudio(previewText, language)
          
          if (audioResult) {
            // Create a preview audio element (not added to messages)
            const previewAudio = new Audio(audioResult.url)
            previewAudio.playbackRate = playbackSpeed
            
            // Auto-play the preview
            previewAudio.play().catch(err => {
              console.log('Auto-play prevented by browser:', err)
            })
            
            console.log('🎤 Real-time preview generated')
          }
        } catch (err) {
          console.error('Preview generation failed:', err)
        } finally {
          setIsGeneratingPreview(false)
        }
      }
    }, 2000) // 2 second debounce

    // Cleanup
    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [textInput, language, realtimePreview, selectedVoice, playbackSpeed, isLoading])

  const downloadAudio = (message: Message, index: number) => {
    if (message.audioBlob) {
      const url = URL.createObjectURL(message.audioBlob)
      const a = document.createElement('a')
      a.href = url
      a.download = `audio-${language}-${Date.now()}.mp3`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
  }

  const clearAllHistory = () => {
    if (messages.length === 0) {
      alert('No history to clear!')
      return
    }

    const confirmed = window.confirm(
      `🗑️ Clear All History?\n\nThis will delete all ${messages.length} generated audio${messages.length > 1 ? 's' : ''} and cannot be undone.\n\nAre you sure?`
    )

    if (confirmed) {
      // Stop all playing audio
      Object.values(audioRefs.current).forEach(audio => {
        if (audio) {
          audio.pause()
          audio.src = ''
        }
      })

      // Revoke all blob URLs
      messages.forEach(msg => {
        if (msg.audioUrl) {
          URL.revokeObjectURL(msg.audioUrl)
        }
      })

      // Clear refs and state
      audioRefs.current = {}
      canvasRefs.current = {}
      setMessages([])
      setCurrentlyPlaying(null)
      
      console.log('✅ History cleared successfully')
    }
  }

  // Handle text file upload
  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    if (!file.name.endsWith('.txt')) {
      alert('Please upload a .txt file')
      return
    }

    try {
      const text = await file.text()
      
      // Split into paragraphs (by double newlines or single newlines)
      const paragraphs = text
        .split(/\n\n+/)
        .map(p => p.trim())
        .filter(p => p.length > 0)

      if (paragraphs.length === 0) {
        alert('No text found in file')
        return
      }

      const confirmed = window.confirm(
        `📄 Process Text File?\n\nFile: ${file.name}\nParagraphs found: ${paragraphs.length}\n\nThis will generate audio for each paragraph.\n\nContinue?`
      )

      if (!confirmed) {
        event.target.value = '' // Reset input
        return
      }

      setIsLoading(true)

      // Process each paragraph
      for (let i = 0; i < paragraphs.length; i++) {
        const paragraph = paragraphs[i]
        
        try {
          console.log(`Processing paragraph ${i + 1}/${paragraphs.length}...`)
          
          const audioResult = await synthesizeAudio(paragraph, language)
          
          if (audioResult) {
            const messageWithAudio: Message = {
              role: 'assistant',
              content: `📄 [Paragraph ${i + 1}/${paragraphs.length}] ${paragraph.substring(0, 100)}${paragraph.length > 100 ? '...' : ''}`,
              timestamp: new Date(),
              audioUrl: audioResult.url,
              audioBlob: audioResult.blob,
              provider: audioResult.provider,
              language: language
            }
            setMessages(prev => [...prev, messageWithAudio])
            
            // Draw waveform after adding message
            setTimeout(() => {
              const index = messages.length + i
              const canvas = canvasRefs.current[index]
              if (canvas && audioResult.blob) {
                drawWaveform(audioResult.blob, canvas)
              }
            }, 100)
          }

          // Small delay between requests to avoid overwhelming the API
          if (i < paragraphs.length - 1) {
            await new Promise(resolve => setTimeout(resolve, 500))
          }
        } catch (err) {
          console.error(`Failed to process paragraph ${i + 1}:`, err)
        }
      }

      alert(`✅ Processed ${paragraphs.length} paragraphs from ${file.name}`)
      event.target.value = '' // Reset input
    } catch (err) {
      console.error('File upload failed:', err)
      alert('Failed to read file. Please try again.')
      event.target.value = '' // Reset input
    } finally {
      setIsLoading(false)
    }
  }

  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!textInput.trim() || isLoading) return

    const userText = textInput.trim()
    setTextInput('')
    setIsLoading(true)

    try {
      if (multiLanguageMode) {
        // Multi-language mode: split and process each segment
        const segments = splitIntoLanguageSegments(userText)
        console.log('🌍 Detected segments:', segments)
        
        if (segments.length === 0) {
          throw new Error('No text segments detected')
        }
        
        // Generate audio for each segment
        const audioSegments: Array<{ blob: Blob, url: string, provider: string }> = []
        
        for (const segment of segments) {
          const audioResult = await synthesizeAudio(segment.text, segment.language)
          if (audioResult) {
            audioSegments.push(audioResult)
          }
        }
        
        if (audioSegments.length > 0) {
          // For now, use the first segment as primary (could be combined later)
          // In a production app, you'd concatenate the audio blobs
          const messageWithAudio: Message = {
            role: 'assistant',
            content: userText + ` 🌍 (${segments.length} language segments)`,
            timestamp: new Date(),
            audioUrl: audioSegments[0].url,
            audioBlob: audioSegments[0].blob,
            provider: audioSegments[0].provider,
            language: segments.map(s => s.language).join(', ')
          }
          setMessages(prev => [...prev, messageWithAudio])
          
          // Play segments sequentially
          for (let i = 0; i < audioSegments.length; i++) {
            const audio = new Audio(audioSegments[i].url)
            audio.playbackRate = playbackSpeed
            
            // Wait for current segment to finish before playing next
            await new Promise<void>((resolve) => {
              audio.onended = () => resolve()
              audio.play().catch(err => {
                console.error('Auto-play failed:', err)
                resolve()
              })
            })
          }
        }
      } else {
        // Normal mode: single language
        const audioResult = await synthesizeAudio(userText, language)
        
        if (audioResult) {
          const messageWithAudio: Message = {
            role: 'assistant',
            content: userText,
            timestamp: new Date(),
            audioUrl: audioResult.url,
            audioBlob: audioResult.blob,
            provider: audioResult.provider,
            language: language
          }
          setMessages(prev => [...prev, messageWithAudio])
        }
      }
    } catch (err) {
      console.error('Failed to generate audio:', err)
      alert('Failed to generate audio. Please check the console for details.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-5xl mx-auto transition-colors duration-300">
      <div className={`${darkMode ? 'bg-gradient-to-br from-gray-900 to-gray-800' : 'bg-gradient-to-br from-white to-blue-50'} rounded-3xl shadow-2xl overflow-hidden transition-colors duration-300`}>
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 relative">
          <h2 className="text-3xl font-bold text-white flex items-center gap-3">
            <span className="text-4xl">🎙️</span>
            Text to Speech Generator
          </h2>
          <p className="text-blue-100 mt-2">Convert your text to natural-sounding speech in multiple languages</p>
          
          {/* Top Right Buttons */}
          <div className="absolute top-6 right-6 flex gap-2">
            {/* Settings Button */}
            <button
              onClick={() => setShowSettings(true)}
              className="p-3 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full transition-all duration-300 group"
              title="API Settings"
            >
              <svg className="w-6 h-6 text-white group-hover:rotate-90 transition-transform duration-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
            
            {/* Dark Mode Toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="p-3 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-full transition-all duration-300 group"
              title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            >
              {darkMode ? (
                <svg className="w-6 h-6 text-yellow-300 group-hover:rotate-180 transition-transform duration-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg className="w-6 h-6 text-white group-hover:rotate-180 transition-transform duration-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
              )}
            </button>
          </div>
        </div>

        <div className="p-8 space-y-6">
          {/* Language, Voice & Speed Selectors */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Language Selector */}
            <div className={`${darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white'} rounded-xl p-6 shadow-md transition-colors duration-300`}>
              <label className={`block text-lg font-semibold ${darkMode ? 'text-gray-200' : 'text-gray-800'} mb-3`}>
                🌍 Language
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className={`w-full px-5 py-4 text-lg ${darkMode ? 'text-gray-200 bg-gray-700 border-gray-600' : 'text-gray-800 bg-white border-gray-300'} border-2 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300`}
              >
                <option value="English" className={darkMode ? 'bg-gray-700 text-gray-200' : 'text-gray-800'}>🇬🇧 English</option>
                <option value="Urdu" className={darkMode ? 'bg-gray-700 text-gray-200' : 'text-gray-800'}>🇵🇰 Urdu (اردو)</option>
                <option value="Sindhi" className={darkMode ? 'bg-gray-700 text-gray-200' : 'text-gray-800'}>🇵🇰 Sindhi (سنڌي)</option>
              </select>
            </div>

            {/* Voice Selector */}
            <div className={`${darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white'} rounded-xl p-6 shadow-md transition-colors duration-300`}>
              <label className={`block text-lg font-semibold ${darkMode ? 'text-gray-200' : 'text-gray-800'} mb-3`}>
                🎤 Voice Style
              </label>
              <select
                value={selectedVoice}
                onChange={(e) => setSelectedVoice(e.target.value)}
                className={`w-full px-5 py-4 text-lg ${darkMode ? 'text-gray-200 bg-gray-700 border-gray-600' : 'text-gray-800 bg-white border-gray-300'} border-2 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300`}
              >
                {availableVoices.map(voice => (
                  <option 
                    key={voice.id} 
                    value={voice.id}
                    className={darkMode ? 'bg-gray-700 text-gray-200' : 'text-gray-800'}
                  >
                    {voice.name}
                  </option>
                ))}
              </select>
            </div>

            {/* Speed Control */}
            <div className={`${darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white'} rounded-xl p-6 shadow-md transition-colors duration-300`}>
              <label className={`block text-lg font-semibold ${darkMode ? 'text-gray-200' : 'text-gray-800'} mb-3`}>
                ⚡ Playback Speed
              </label>
              <select
                value={playbackSpeed}
                onChange={(e) => setPlaybackSpeed(Number(e.target.value))}
                className={`w-full px-5 py-4 text-lg ${darkMode ? 'text-gray-200 bg-gray-700 border-gray-600' : 'text-gray-800 bg-white border-gray-300'} border-2 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300`}
              >
                {speedOptions.map(speed => (
                  <option 
                    key={speed.value} 
                    value={speed.value}
                    className={darkMode ? 'bg-gray-700 text-gray-200' : 'text-gray-800'}
                  >
                    {speed.icon} {speed.label}
                  </option>
                ))}
              </select>
              <p className={`mt-2 text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                {playbackSpeed < 1 ? 'Great for learning' : playbackSpeed > 1 ? 'Save time' : 'Standard speed'}
              </p>
            </div>
          </div>

          {/* Text Input Form with Clear History Button */}
          <div className={`${darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white'} rounded-xl p-6 shadow-md transition-colors duration-300`}>
            {/* Header with Title and Clear Button */}
            <div className="flex justify-between items-center mb-4">
              <label className={`text-lg font-semibold ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                ✍️ Enter Your Text
              </label>
              
              {messages.length > 0 && (
                <button
                  onClick={clearAllHistory}
                  className="flex items-center gap-2 px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg transition-all duration-300 text-sm font-medium shadow-md hover:shadow-lg transform hover:scale-105"
                  title="Clear all generated audio"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  Clear All ({messages.length})
                </button>
              )}
            </div>

            {/* Feature Toggles - Now Prominent */}
            <div className={`flex flex-wrap items-center gap-4 mb-4 p-3 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
              {/* Real-time Preview Toggle */}
              <label className="flex items-center gap-2 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={realtimePreview}
                  onChange={(e) => setRealtimePreview(e.target.checked)}
                  className="w-5 h-5 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 focus:ring-2 cursor-pointer"
                />
                <span className={`text-sm font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'} group-hover:text-blue-600 transition-colors whitespace-nowrap`}>
                  🎤 Real-time Preview
                </span>
                {isGeneratingPreview && (
                  <span className="flex items-center gap-1 text-xs text-blue-600">
                    <svg className="animate-spin h-3 w-3" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Generating...
                  </span>
                )}
              </label>

              {/* Divider */}
              <div className={`h-6 w-px ${darkMode ? 'bg-gray-600' : 'bg-gray-300'}`}></div>

              {/* Multi-language Mode Toggle */}
              <label className="flex items-center gap-2 cursor-pointer group">
                <input
                  type="checkbox"
                  checked={multiLanguageMode}
                  onChange={(e) => setMultiLanguageMode(e.target.checked)}
                  className="w-5 h-5 text-purple-600 bg-gray-100 border-gray-300 rounded focus:ring-purple-500 focus:ring-2 cursor-pointer"
                />
                <span className={`text-sm font-medium ${darkMode ? 'text-gray-200' : 'text-gray-700'} group-hover:text-purple-600 transition-colors whitespace-nowrap`}>
                  🌍 Multi-language Mode
                </span>
              </label>
            </div>
            
            {/* Info Messages */}
            {realtimePreview && (
              <div className={`mb-3 p-3 rounded-lg ${darkMode ? 'bg-blue-900/30 border border-blue-700' : 'bg-blue-50 border border-blue-200'} transition-colors`}>
                <p className={`text-sm ${darkMode ? 'text-blue-300' : 'text-blue-700'} flex items-center gap-2`}>
                  <span className="text-lg">⚡</span>
                  <span>Real-time preview enabled! Audio will generate automatically 2 seconds after you stop typing.</span>
                </p>
              </div>
            )}
            
            {multiLanguageMode && (
              <div className={`mb-3 p-3 rounded-lg ${darkMode ? 'bg-purple-900/30 border border-purple-700' : 'bg-purple-50 border border-purple-200'} transition-colors`}>
                <p className={`text-sm ${darkMode ? 'text-purple-300' : 'text-purple-700'} flex items-center gap-2`}>
                  <span className="text-lg">🌍</span>
                  <span>Multi-language mode enabled! Mix English, Urdu (اردو), and Sindhi (سنڌي) naturally. Each language will be auto-detected and spoken correctly.</span>
                </p>
              </div>
            )}
            <form onSubmit={handleTextSubmit} className="space-y-4">
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder={`Type or paste your text in ${language}...`}
                rows={4}
                className={`w-full px-5 py-4 text-lg ${darkMode ? 'text-gray-200 bg-gray-700 border-gray-600 placeholder-gray-500' : 'text-gray-900 bg-white border-gray-300 placeholder-gray-400'} border-2 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-300 resize-none`}
                disabled={isLoading}
              />
              <div className="flex items-center justify-between">
                <span className={`text-sm ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  {textInput.length} characters
                </span>
                <button
                  type="submit"
                  disabled={isLoading || !textInput.trim()}
                  className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-400 text-white text-lg font-semibold rounded-xl transition shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 disabled:transform-none flex items-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Generating...
                    </>
                  ) : (
                    <>
                      <span className="text-2xl">🔊</span>
                      Generate Speech
                    </>
                  )}
                </button>
              </div>
            </form>

            {/* File Upload */}
            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <label className={`flex items-center justify-center gap-3 px-6 py-3 border-2 border-dashed ${darkMode ? 'border-gray-600 hover:border-blue-500' : 'border-gray-300 hover:border-blue-500'} rounded-xl cursor-pointer transition-all duration-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 group`}>
                <svg className="w-6 h-6 text-gray-500 group-hover:text-blue-600 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span className={`font-medium ${darkMode ? 'text-gray-300' : 'text-gray-700'} group-hover:text-blue-600 transition-colors`}>
                  📄 Upload .txt File (Batch Process)
                </span>
                <input
                  type="file"
                  accept=".txt"
                  onChange={handleFileUpload}
                  className="hidden"
                  disabled={isLoading}
                />
              </label>
              <p className={`text-xs ${darkMode ? 'text-gray-500' : 'text-gray-400'} text-center mt-2`}>
                Upload a text file to convert multiple paragraphs at once
              </p>
            </div>
          </div>

          {/* Generated Audio List */}
          {messages.length > 0 && (
            <div className={`${darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white'} rounded-xl p-6 shadow-md transition-colors duration-300`}>
              <h3 className={`text-xl font-semibold ${darkMode ? 'text-gray-200' : 'text-gray-800'} mb-4 flex items-center gap-2`}>
                <span>🎵</span>
                Generated Audio Files ({messages.length})
              </h3>
              <div className="space-y-3 max-h-[500px] overflow-y-auto pr-2">
                {messages.slice().reverse().map((msg, idx) => {
                  const actualIndex = messages.length - 1 - idx
                  return (
                    <div key={actualIndex} className={`${darkMode ? 'bg-gray-700 border-gray-600 hover:border-blue-500' : 'bg-gradient-to-r from-gray-50 to-blue-50 border-gray-200 hover:border-blue-300'} rounded-lg p-4 border-2 transition-all duration-300`}>
                      <div className="flex items-start gap-4">
                        <div className="flex-1 min-w-0">
                          <p className={`${darkMode ? 'text-gray-200' : 'text-gray-700'} font-medium mb-2 break-words`}>
                            {msg.content}
                          </p>
                          
                          {/* Waveform Visualization */}
                          {msg.audioBlob && (
                            <div className="my-3">
                              <canvas
                                ref={el => {
                                  if (el) {
                                    canvasRefs.current[actualIndex] = el
                                    // Draw waveform when canvas is mounted
                                    drawWaveform(msg.audioBlob!, el)
                                  }
                                }}
                                width={600}
                                height={60}
                                className="w-full h-15 rounded-lg bg-gray-100 dark:bg-gray-800"
                              />
                            </div>
                          )}

                          <div className={`flex flex-wrap items-center gap-2 text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                            <span className={`px-2 py-1 ${darkMode ? 'bg-blue-900 text-blue-300' : 'bg-blue-100 text-blue-700'} rounded-full`}>
                              {language}
                            </span>
                            <span className={`px-2 py-1 ${darkMode ? 'bg-purple-900 text-purple-300' : 'bg-purple-100 text-purple-700'} rounded-full`}>
                              {availableVoices.find(v => v.id === selectedVoice)?.name.split(' ')[1] || msg.provider || 'uplift'}
                            </span>
                            <span>{msg.timestamp.toLocaleTimeString()}</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-2 flex-shrink-0">
                          {/* Play/Pause Button */}
                          <button
                            onClick={() => playAudio(actualIndex)}
                            className="p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-full transition shadow-md hover:shadow-lg"
                            title={currentlyPlaying === actualIndex ? 'Pause' : 'Play'}
                          >
                            {currentlyPlaying === actualIndex ? (
                              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M6 4h4v16H6V4zm8 0h4v16h-4V4z"/>
                              </svg>
                            ) : (
                              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                                <path d="M8 5v14l11-7z"/>
                              </svg>
                            )}
                          </button>
                          {/* Download Button */}
                          <button
                            onClick={() => downloadAudio(msg, actualIndex)}
                            className="p-3 bg-green-600 hover:bg-green-700 text-white rounded-full transition shadow-md hover:shadow-lg"
                            title="Download MP3"
                          >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                            </svg>
                          </button>
                        </div>
                      </div>
                      {/* Hidden Audio Element */}
                      <audio
                        ref={(el) => {
                          if (el) audioRefs.current[actualIndex] = el
                        }}
                        src={msg.audioUrl}
                        onEnded={() => setCurrentlyPlaying(null)}
                        className="hidden"
                      />
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {messages.length === 0 && !isLoading && (
            <div className={`text-center py-12 ${darkMode ? 'bg-gray-800 border border-gray-700' : 'bg-white'} rounded-xl shadow-md transition-colors duration-300`}>
              <div className="text-6xl mb-4">🎤</div>
              <p className={`text-xl ${darkMode ? 'text-gray-300' : 'text-gray-600'} font-medium mb-2`}>Ready to Generate Speech!</p>
              <p className={`${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>Enter your text above and click "Generate Speech"</p>
              <div className={`mt-6 flex justify-center gap-4 text-sm ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                <span>✨ Powered by Uplift AI</span>
                <span>•</span>
                <span>~300ms latency</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fadeIn">
          <div className={`${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white'} rounded-2xl shadow-2xl max-w-2xl w-full mx-4 border-2 transform transition-all`}>
            {/* Modal Header */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-6 rounded-t-2xl">
              <div className="flex items-center justify-between">
                <h3 className="text-2xl font-bold text-white flex items-center gap-3">
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  API Settings
                </h3>
                <button
                  onClick={() => setShowSettings(false)}
                  className="p-2 hover:bg-white/20 rounded-full transition-colors"
                  title="Close"
                >
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Modal Body */}
            <div className="p-6 space-y-6">
              {/* Current Status */}
              {currentSettings && (
                <div className={`p-4 rounded-lg ${darkMode ? 'bg-gray-700' : 'bg-gray-50'} space-y-2`}>
                  <h4 className={`font-semibold ${darkMode ? 'text-gray-200' : 'text-gray-800'} mb-3`}>📊 Current API Status</h4>
                  
                  <div className="flex items-center justify-between">
                    <span className={`${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>🚀 Uplift AI:</span>
                    <div className="flex items-center gap-2">
                      <code className={`px-3 py-1 rounded text-sm ${darkMode ? 'bg-gray-600 text-gray-200' : 'bg-white text-gray-800'}`}>
                        {currentSettings.uplift_api_key}
                      </code>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${currentSettings.uplift_active ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}`}>
                        {currentSettings.uplift_active ? '✓ Active' : '✗ Inactive'}
                      </span>
                    </div>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className={`${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>🤖 OpenAI:</span>
                    <div className="flex items-center gap-2">
                      <code className={`px-3 py-1 rounded text-sm ${darkMode ? 'bg-gray-600 text-gray-200' : 'bg-white text-gray-800'}`}>
                        {currentSettings.openai_api_key}
                      </code>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${currentSettings.openai_active ? 'bg-green-500 text-white' : 'bg-yellow-500 text-white'}`}>
                        {currentSettings.openai_active ? '✓ Active' : '⚠ Fallback'}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Info Box */}
              <div className={`p-4 rounded-lg ${darkMode ? 'bg-blue-900/30 border border-blue-700' : 'bg-blue-50 border border-blue-200'}`}>
                <p className={`text-sm ${darkMode ? 'text-blue-300' : 'text-blue-700'}`}>
                  💡 <strong>Tip:</strong> Update your API keys below. Changes are saved immediately and applied to new requests.
                </p>
              </div>

              {/* Uplift AI Key Input */}
              <div>
                <label className={`block font-semibold ${darkMode ? 'text-gray-200' : 'text-gray-800'} mb-2`}>
                  🚀 Uplift AI API Key
                </label>
                <input
                  type="password"
                  value={upliftApiKey}
                  onChange={(e) => setUpliftApiKey(e.target.value)}
                  placeholder="sk_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                  className={`w-full px-4 py-3 rounded-lg border-2 ${darkMode ? 'bg-gray-700 border-gray-600 text-gray-200 placeholder-gray-500' : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400'} focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors font-mono text-sm`}
                />
                <p className={`mt-2 text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  Get your key from: <a href="https://www.upliftai.org/" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">upliftai.org</a>
                </p>
              </div>

              {/* OpenAI Key Input */}
              <div>
                <label className={`block font-semibold ${darkMode ? 'text-gray-200' : 'text-gray-800'} mb-2`}>
                  🤖 OpenAI API Key (Fallback)
                </label>
                <input
                  type="password"
                  value={openaiApiKey}
                  onChange={(e) => setOpenaiApiKey(e.target.value)}
                  placeholder="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                  className={`w-full px-4 py-3 rounded-lg border-2 ${darkMode ? 'bg-gray-700 border-gray-600 text-gray-200 placeholder-gray-500' : 'bg-white border-gray-300 text-gray-900 placeholder-gray-400'} focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors font-mono text-sm`}
                />
                <p className={`mt-2 text-xs ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
                  Get your key from: <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">platform.openai.com</a>
                </p>
              </div>
            </div>

            {/* Modal Footer */}
            <div className={`p-6 ${darkMode ? 'bg-gray-700/50' : 'bg-gray-50'} rounded-b-2xl flex gap-3`}>
              <button
                onClick={() => setShowSettings(false)}
                className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors ${darkMode ? 'bg-gray-600 hover:bg-gray-500 text-gray-200' : 'bg-gray-200 hover:bg-gray-300 text-gray-800'}`}
              >
                Cancel
              </button>
              <button
                onClick={saveApiKeys}
                disabled={isSavingSettings}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 disabled:from-gray-400 disabled:to-gray-400 text-white font-medium rounded-lg transition-all shadow-lg hover:shadow-xl flex items-center justify-center gap-2"
              >
                {isSavingSettings ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Saving...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Save Changes
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
