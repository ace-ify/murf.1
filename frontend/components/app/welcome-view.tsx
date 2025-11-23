import { Button } from '@/components/livekit/button';

function StarbucksLogo() {
  return (
    <div className="relative">
      {/* Outer glow effect */}
      <div className="absolute inset-0 bg-primary/20 rounded-full blur-2xl animate-glow"></div>
      
      <svg
        width="120"
        height="120"
        viewBox="0 0 120 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="relative text-primary mb-6 size-28 drop-shadow-2xl animate-in zoom-in duration-700"
      >
        {/* Outer circle - Starbucks style */}
        <circle cx="60" cy="60" r="56" stroke="currentColor" strokeWidth="3" fill="none" className="opacity-80"/>\n        <circle cx="60" cy="60" r="50" stroke="currentColor" strokeWidth="2" fill="none" className="opacity-40"/>\n        
        {/* Coffee cup with rich details */}
        <defs>
          <linearGradient id="coffeeGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="currentColor" stopOpacity="0.3"/>
            <stop offset="100%" stopColor="currentColor" stopOpacity="0.15"/>
          </linearGradient>
        </defs>
        
        <path
          d="M35 50 C35 47 37 45 40 45 L80 45 C83 45 85 47 85 50 L82 85 C82 90 78 95 60 95 C42 95 38 90 38 85 L35 50 Z"
          fill="url(#coffeeGradient)"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinejoin="round"
        />
        
        {/* Coffee liquid inside */}
        <ellipse cx="60" cy="52" rx="22" ry="5" fill="currentColor" opacity="0.5"/>
        
        {/* Steam lines - animated */}
        <g className="animate-steam" style={{ transformOrigin: '50px 35px' }}>
          <path
            d="M48 38 Q48 30 52 26"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            opacity="0.7"
          />
        </g>
        <g className="animate-steam" style={{ transformOrigin: '60px 35px', animationDelay: '0.3s' }}>
          <path
            d="M60 36 Q60 26 64 22"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            opacity="0.7"
          />
        </g>
        <g className="animate-steam" style={{ transformOrigin: '72px 35px', animationDelay: '0.6s' }}>
          <path
            d="M72 38 Q72 30 68 26"
            stroke="currentColor"
            strokeWidth="2.5"
            strokeLinecap="round"
            opacity="0.7"
          />
        </g>
        
        {/* Cup handle */}
        <path
          d="M85 55 Q94 55 94 65 Q94 75 85 75"
          stroke="currentColor"
          strokeWidth="3"
          fill="none"
          strokeLinecap="round"
        />
        
        {/* Decorative stars - Starbucks inspired */}
        <circle cx="60" cy="70" r="2.5" fill="currentColor" opacity="0.9"/>
        <circle cx="53" cy="65" r="1.5" fill="currentColor" opacity="0.7"/>
        <circle cx="67" cy="65" r="1.5" fill="currentColor" opacity="0.7"/>
      </svg>
    </div>
  );
}

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref} className="relative min-h-screen overflow-y-auto bg-gradient-to-br from-[#F9F7F4] via-[#F4EDE4] to-[#E8DDD1]">
      {/* Rich coffee-themed background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Large coffee bean patterns */}
        {[...Array(15)].map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full opacity-[0.04]"
            style={{
              width: `${Math.random() * 100 + 50}px`,
              height: `${Math.random() * 150 + 80}px`,
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              background: `radial-gradient(ellipse, #8B5A3C, #6B5947)`,
              transform: `rotate(${Math.random() * 360}deg)`,
              animation: `bean-spin ${15 + Math.random() * 10}s linear infinite`,
              animationDelay: `${Math.random() * 5}s`,
            }}
          />
        ))}
        
        {/* Floating steam/smoke effects */}
        <div className="absolute top-0 left-1/4 w-64 h-64 bg-[#00704A]/5 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-20 right-1/4 w-80 h-80 bg-[#D4A574]/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
        <div className="absolute top-1/3 right-1/3 w-48 h-48 bg-[#8B5A3C]/5 rounded-full blur-2xl animate-float" style={{ animationDelay: '4s' }}></div>
      </div>

      {/* Hero Section */}
      <section className="relative z-10 flex flex-col items-center justify-center min-h-screen px-4 py-12">
        {/* Top brand strip */}
        <div className="absolute top-0 left-0 right-0 bg-gradient-to-b from-[#00704A]/10 to-transparent h-32 backdrop-blur-sm"></div>
        
        <div className="max-w-6xl mx-auto w-full">
          {/* Logo and Hero Content */}
          <div className="text-center mb-12">
            <StarbucksLogo />
            
            {/* Main heading with coffee gradient */}
            <h1 className="text-5xl md:text-7xl font-black mb-4 tracking-tight animate-in fade-in slide-in-from-bottom-4 duration-700"
                style={{
                  background: 'linear-gradient(135deg, #00704A 0%, #1E9668 50%, #8B5A3C 100%)',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  backgroundClip: 'text',
                }}>
              Starbucks Voice
            </h1>
            <h2 className="text-3xl md:text-5xl font-bold text-[#3D2817] mb-6 tracking-tight animate-in fade-in slide-in-from-bottom-4 duration-700" style={{ animationDelay: '0.1s' }}>
              Order with Your Voice
            </h2>

            {/* Subheading */}
            <p className="text-[#6B5947] max-w-2xl mx-auto text-lg md:text-xl leading-relaxed font-medium mb-3 animate-in fade-in slide-in-from-bottom-4 duration-700" style={{ animationDelay: '0.2s' }}>
              Experience the future of coffee ordering. Speak naturally, order effortlessly.
            </p>
          </div>

          {/* Coffee showcase cards - Image placeholders */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto mb-12 animate-in fade-in duration-700" style={{ animationDelay: '0.3s' }}>
            {[
              { name: 'Caramel\nMacchiato', color: '#D4A574' },
              { name: 'Iced\nLatte', color: '#C7A27C' },
              { name: 'Mocha\nFrappuccino', color: '#8B5A3C' },
              { name: 'Cold\nBrew', color: '#6B5947' }
            ].map((drink, i) => (
              <div 
                key={drink.name}
                className="group relative bg-white/60 backdrop-blur-sm rounded-2xl p-4 border-2 border-[#E8DDD1] hover:border-[#00704A]/30 transition-all duration-300 hover:scale-105 hover:shadow-xl cursor-default overflow-hidden"
                style={{ animationDelay: `${0.4 + i * 0.1}s` }}
              >
                {/* Coffee cup illustration placeholder */}
                <div className="relative aspect-square mb-3 rounded-xl overflow-hidden bg-gradient-to-br from-white to-[#F4EDE4] flex items-center justify-center">
                  <div 
                    className="w-16 h-20 rounded-lg opacity-20"
                    style={{ backgroundColor: drink.color }}
                  >
                  </div>
                  {/* Coffee cup SVG icon */}
                  <svg className="absolute w-12 h-12" viewBox="0 0 48 48" fill="none">
                    <path d="M14 20 C14 18 15 17 17 17 L31 17 C33 17 34 18 34 20 L32 35 C32 38 29 40 24 40 C19 40 16 38 16 35 L14 20 Z" fill={drink.color} opacity="0.6"/>
                    <ellipse cx="24" cy="19" rx="8" ry="2" fill={drink.color} opacity="0.8"/>
                    <path d="M34 23 Q38 23 38 27 Q38 31 34 31" stroke={drink.color} strokeWidth="2" fill="none"/>
                  </svg>
                </div>
                <p className="text-center text-sm font-bold text-[#3D2817] whitespace-pre-line leading-tight">
                  {drink.name}
                </p>
                
                {/* Hover effect overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-[#00704A]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl"></div>
              </div>
            ))}
          </div>

          {/* Features grid */}
          <div className="flex flex-wrap gap-3 justify-center mb-10 animate-in fade-in duration-700" style={{ animationDelay: '0.5s' }}>
            <div className="bg-gradient-to-r from-[#00704A] to-[#1E9668] text-white px-6 py-3 rounded-full text-sm font-bold border-2 border-[#00704A] shadow-lg hover:shadow-xl transition-all hover:scale-105 cursor-default">
              ☕ All Menu Items
            </div>
            <div className="bg-white/80 backdrop-blur-sm text-[#00704A] px-6 py-3 rounded-full text-sm font-bold border-2 border-[#00704A]/20 shadow-md hover:shadow-lg transition-all hover:scale-105 cursor-default">
              🎙️ Voice Powered
            </div>
            <div className="bg-gradient-to-r from-[#D4A574] to-[#C7A27C] text-white px-6 py-3 rounded-full text-sm font-bold border-2 border-[#D4A574] shadow-lg hover:shadow-xl transition-all hover:scale-105 cursor-default">
              ⚡ Instant Order
            </div>
            <div className="bg-white/80 backdrop-blur-sm text-[#8B5A3C] px-6 py-3 rounded-full text-sm font-bold border-2 border-[#8B5A3C]/20 shadow-md hover:shadow-lg transition-all hover:scale-105 cursor-default">
              ✨ AI Powered
            </div>
          </div>

          {/* CTA Button - Hero style */}
          <div className="text-center animate-in fade-in zoom-in duration-700" style={{ animationDelay: '0.6s' }}>
            <Button 
              variant="primary" 
              size="lg" 
              onClick={onStartCall} 
              className="group relative px-16 py-8 text-xl font-black rounded-full shadow-2xl hover:shadow-[0_20px_60px_rgba(0,112,74,0.4)] transition-all duration-500 hover:scale-110 overflow-hidden"
              style={{
                background: 'linear-gradient(135deg, #00704A 0%, #1E9668 100%)',
                border: '3px solid rgba(255,255,255,0.3)',
              }}
            >
              <span className="relative z-10 flex items-center gap-3">
                <span className="text-3xl">🎤</span>
                {startButtonText}
                <svg className="w-6 h-6 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
              {/* Shine effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
            </Button>
            
            <p className="mt-6 text-[#6B5947] text-sm font-medium">
              🔒 Secure • ⚡ Instant • 🎯 Accurate
            </p>
          </div>

          {/* Social proof / stats */}
          <div className="mt-16 grid grid-cols-3 gap-6 max-w-2xl mx-auto text-center animate-in fade-in duration-700" style={{ animationDelay: '0.8s' }}>
            <div className="bg-white/40 backdrop-blur-sm rounded-2xl p-6 border border-[#E8DDD1]">
              <div className="text-3xl font-black text-[#00704A] mb-2">100+</div>
              <div className="text-sm font-semibold text-[#6B5947]">Drink Options</div>
            </div>
            <div className="bg-white/40 backdrop-blur-sm rounded-2xl p-6 border border-[#E8DDD1]">
              <div className="text-3xl font-black text-[#8B5A3C] mb-2">24/7</div>
              <div className="text-sm font-semibold text-[#6B5947]">Always Open</div>
            </div>
            <div className="bg-white/40 backdrop-blur-sm rounded-2xl p-6 border border-[#E8DDD1]">
              <div className="text-3xl font-black text-[#D4A574] mb-2">5★</div>
              <div className="text-sm font-semibold text-[#6B5947]">AI Experience</div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <div className="fixed bottom-0 left-0 right-0 z-20 bg-gradient-to-t from-[#F9F7F4] via-[#F9F7F4]/95 to-transparent backdrop-blur-md py-6 border-t border-[#E8DDD1]/50">
        <div className="flex flex-col items-center gap-2">
          <div className="flex items-center gap-2">
            <span className="text-2xl">⚡</span>
            <p className="text-[#3D2817] text-sm md:text-base font-bold">
              Powered by <span className="text-[#00704A]">Murf Falcon TTS</span>
            </p>
          </div>
          <p className="text-[#6B5947] text-xs font-medium">
            #MurfAIVoiceAgentsChallenge • #10DaysofAIVoiceAgents
          </p>
        </div>
      </div>
    </div>
  );
};
