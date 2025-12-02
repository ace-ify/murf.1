'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import type { AppConfig } from '@/app-config';
import { ChatTranscript } from '@/components/app/chat-transcript';
import { PreConnectMessage } from '@/components/app/preconnect-message';
import { TileLayout } from '@/components/app/tile-layout';
import {
  AgentControlBar,
  type ControlBarControls,
} from '@/components/livekit/agent-control-bar/agent-control-bar';
import { useChatMessages } from '@/hooks/useChatMessages';
import { useConnectionTimeout } from '@/hooks/useConnectionTimout';
import { useDebugMode } from '@/hooks/useDebug';
import { cn } from '@/lib/utils';
import { ScrollArea } from '../livekit/scroll-area/scroll-area';

const MotionBottom = motion.create('div');

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';
const BOTTOM_VIEW_MOTION_PROPS = {
  variants: {
    visible: { opacity: 1, y: 0 },
    hidden: { opacity: 0, y: 20 },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: { duration: 0.5, ease: [0.16, 1, 0.3, 1] },
};

interface SessionViewProps {
  appConfig: AppConfig;
}

export const SessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  useConnectionTimeout(200_000);
  useDebugMode({ enabled: IN_DEVELOPMENT });

  const messages = useChatMessages();
  const [chatOpen, setChatOpen] = useState(false);
  const [controlsVisible, setControlsVisible] = useState(true);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout>(null);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsVideoInput,
  };

  // Auto-hide controls logic
  useEffect(() => {
    const handleMouseMove = () => {
      setControlsVisible(true);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
      timeoutRef.current = setTimeout(() => setControlsVisible(false), 3000);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, []);

  useEffect(() => {
    const lastMessage = messages.at(-1);
    const lastMessageIsLocal = lastMessage?.from?.isLocal === true;

    if (scrollAreaRef.current && lastMessageIsLocal) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <section className="relative h-screen w-full bg-black overflow-hidden" {...props}>

      {/* Dynamic Nebula Background */}
      <div className="absolute inset-0 z-0 overflow-hidden">
        {/* Deep Base */}
        <div className="absolute inset-0 bg-black" />

        {/* Nebula Layer 1: Deep Purple */}
        <div className="absolute top-[-20%] left-[-20%] w-[80%] h-[80%] rounded-full bg-purple-900/20 blur-[120px] animate-nebula-drift" />

        {/* Nebula Layer 2: Midnight Blue */}
        <div className="absolute bottom-[-20%] right-[-20%] w-[80%] h-[80%] rounded-full bg-blue-900/20 blur-[120px] animate-nebula-drift" style={{ animationDelay: '-5s', animationDirection: 'reverse' }} />

        {/* Nebula Layer 3: Pulse Core */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-[60%] h-[60%] rounded-full bg-indigo-900/10 blur-[100px] animate-nebula-pulse" />
        </div>

        {/* Grid Overlay for Texture */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:100px_100px] opacity-20" />
      </div>

      {/* Full Screen Visualizer */}
      <div className="absolute inset-0 flex items-center justify-center z-10">
        <div className="w-full h-full max-w-[90%] max-h-[90%] flex items-center justify-center">
          <TileLayout chatOpen={chatOpen} />
        </div>
      </div>

      {/* Minimal Status Indicator */}
      <div className="absolute top-8 left-1/2 -translate-x-1/2 z-20 opacity-50">
        <div className="size-1.5 rounded-full bg-white animate-pulse" />
      </div>

      {/* Chat Overlay (Cinematic) */}
      <AnimatePresence>
        {chatOpen && (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            className="absolute right-0 top-0 bottom-0 w-full md:w-[400px] bg-gradient-to-l from-black via-black/80 to-transparent z-30 p-8 flex flex-col justify-end"
          >
            <ScrollArea ref={scrollAreaRef} className="h-full mask-image-b">
              <ChatTranscript
                hidden={!chatOpen}
                messages={messages}
                className="space-y-6"
              />
            </ScrollArea>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Controls */}
      <AnimatePresence>
        {controlsVisible && (
          <MotionBottom
            {...BOTTOM_VIEW_MOTION_PROPS}
            className="fixed inset-x-0 bottom-12 z-50 flex justify-center pointer-events-none"
          >
            <div className="pointer-events-auto bg-white/5 border border-white/10 backdrop-blur-md rounded-full px-6 py-3 shadow-2xl">
              <AgentControlBar controls={controls} onChatOpenChange={setChatOpen} />
            </div>
          </MotionBottom>
        )}
      </AnimatePresence>

    </section>
  );
};
