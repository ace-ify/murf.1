import { Button } from '@/components/livekit/button';
import { Mic } from 'lucide-react';

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref} className="relative flex h-screen w-full flex-col items-center justify-center bg-black text-white overflow-hidden">

      {/* Background Video */}
      <div className="absolute inset-0 z-0">
        <video
          autoPlay
          loop
          muted
          playsInline
          className="h-full w-full object-cover opacity-60 scale-105"
        >
          <source src="/bg-video.mp4" type="video/mp4" />
        </video>
        {/* Cinematic Overlay/Vignette */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-black/80" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_transparent_0%,_black_120%)]" />
      </div>

      <div className="relative z-10 flex flex-col items-center gap-12 animate-fade-in-slow">

        {/* Minimal Icon */}
        <div className="size-16 rounded-full border border-white/10 flex items-center justify-center bg-white/5 backdrop-blur-sm">
          <Mic className="size-6 text-white/80" />
        </div>

        {/* Massive Typography */}
        <div className="text-center space-y-4">
          <h1 className="text-6xl md:text-9xl font-black tracking-tighter text-white mix-blend-overlay drop-shadow-2xl">
            IMPROV
            <br />
            BATTLE
          </h1>
          <p className="text-sm md:text-base text-white/60 uppercase tracking-[0.3em] font-medium drop-shadow-md">
            A Voice Interactive Experience
          </p>
        </div>

        {/* Primary Action */}
        <Button
          variant="outline"
          size="lg"
          onClick={onStartCall}
          className="h-16 px-12 text-lg font-bold tracking-widest uppercase border-white/30 bg-white/5 hover:bg-white hover:text-black backdrop-blur-md transition-all duration-500 rounded-none"
        >
          {startButtonText}
        </Button>
      </div>

      {/* Footer Minimal */}
      <div className="absolute bottom-8 text-[10px] text-white/40 uppercase tracking-widest z-10">
        Headphones Recommended
      </div>
    </div>
  );
};

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}
