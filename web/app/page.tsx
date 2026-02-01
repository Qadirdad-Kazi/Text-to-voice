'use client'

import { useState } from 'react'
import VoiceAgent from '@/components/VoiceAgent'

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-100 via-purple-50 to-pink-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 transition-colors duration-300">
      <div className="container mx-auto px-4 py-8">
        <VoiceAgent />

        <footer className="mt-12 text-center text-gray-600 dark:text-gray-400 transition-colors duration-300">
          <p className="text-sm flex items-center justify-center gap-2 flex-wrap">
            <span className="font-semibold text-gray-800 dark:text-gray-200">🏠 100% Self-Hosted Voice Agent</span>
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
            Supports English, Urdu (اردو), and Sindhi (سنڌي) • No External APIs Required
          </p>
        </footer>
      </div>
    </main>
  )
}

