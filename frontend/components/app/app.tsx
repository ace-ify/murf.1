'use client';

import { RoomAudioRenderer, StartAudio } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { SessionProvider } from '@/components/app/session-provider';
import { ViewController } from '@/components/app/view-controller';
import { Toaster } from '@/components/livekit/toaster';

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  return (
    <SessionProvider appConfig={appConfig}>
      <main className="relative grid h-svh grid-cols-1 place-content-center bg-gradient-to-br from-[#F9F7F4] via-[#F4EDE4] to-[#E8DDD1]">
        {/* Rich coffee shop atmosphere */}
        <div className="absolute inset-0 overflow-hidden opacity-[0.03] pointer-events-none">
          {/* Coffee beans with realistic placement */}
          {[...Array(25)].map((_, i) => (
            <div
              key={i}
              className="absolute rounded-full animate-bean-spin"
              style={{
                width: `${20 + Math.random() * 30}px`,
                height: `${30 + Math.random() * 50}px`,
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                background: `radial-gradient(ellipse, #8B5A3C, #6B5947)`,
                transform: `rotate(${Math.random() * 360}deg)`,
                opacity: Math.random() * 0.6 + 0.3,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${15 + Math.random() * 10}s`,
              }}
            />
          ))}
        </div>
        <ViewController />
      </main>
      <StartAudio label="Start Audio" />
      <RoomAudioRenderer />
      <Toaster />
    </SessionProvider>
  );
}
