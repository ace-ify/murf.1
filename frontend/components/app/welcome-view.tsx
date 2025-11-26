'use client';

import { Button } from '@/components/livekit/button';
import { useEffect, useState } from 'react';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

// Animated counter hook
function useCounter(end: number, duration: number = 2000, start: number = 0) {
  const [count, setCount] = useState(start);
  
  useEffect(() => {
    let startTime: number;
    let animationFrame: number;
    
    const animate = (timestamp: number) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      setCount(Math.floor(progress * (end - start) + start));
      
      if (progress < 1) {
        animationFrame = requestAnimationFrame(animate);
      }
    };
    
    animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, [end, duration, start]);
  
  return count;
}

// Floating glasses animation component
function FloatingGlasses({ className, delay = 0 }: { className?: string; delay?: number }) {
  return (
    <div 
      className={`absolute opacity-10 ${className}`}
      style={{ 
        animation: `float 6s ease-in-out infinite`,
        animationDelay: `${delay}s`
      }}
    >
      <svg viewBox="0 0 60 30" className="w-full h-full" fill="none" stroke="currentColor" strokeWidth="1.5">
        <ellipse cx="15" cy="15" rx="12" ry="10"/>
        <ellipse cx="45" cy="15" rx="12" ry="10"/>
        <path d="M27 15 Q30 10 33 15"/>
      </svg>
    </div>
  );
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  const [isVisible, setIsVisible] = useState(false);
  const customerCount = useCounter(40, 2000);
  const storeCount = useCounter(2000, 2500);
  const cityCount = useCounter(300, 2000);
  
  useEffect(() => {
    setIsVisible(true);
  }, []);

  return (
    <div ref={ref} className="min-h-screen bg-white overflow-hidden">
      {/* CSS Animations */}
      <style jsx>{`
        @keyframes float {
          0%, 100% { transform: translateY(0) rotate(0deg); }
          50% { transform: translateY(-20px) rotate(5deg); }
        }
        @keyframes pulse-ring {
          0% { transform: scale(1); opacity: 0.4; }
          100% { transform: scale(1.5); opacity: 0; }
        }
        @keyframes slide-up {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fade-in {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        .animate-slide-up {
          animation: slide-up 0.8s ease-out forwards;
        }
        .animate-fade-in {
          animation: fade-in 1s ease-out forwards;
        }
      `}</style>

      {/* Floating Background Elements */}
      <div className="fixed inset-0 pointer-events-none text-[#329c92]">
        <FloatingGlasses className="w-24 h-12 top-[15%] left-[5%]" delay={0} />
        <FloatingGlasses className="w-16 h-8 top-[25%] right-[10%]" delay={1} />
        <FloatingGlasses className="w-20 h-10 bottom-[30%] left-[8%]" delay={2} />
        <FloatingGlasses className="w-14 h-7 top-[60%] right-[5%]" delay={0.5} />
        <FloatingGlasses className="w-12 h-6 bottom-[15%] right-[15%]" delay={1.5} />
      </div>

      {/* Gradient Orbs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-[#329c92]/5 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-[#329c92]/5 rounded-full blur-3xl"></div>
      </div>

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 bg-white/90 backdrop-blur-md z-50 border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2 group cursor-pointer">
            <div className="w-9 h-9 bg-[#329c92] rounded-lg flex items-center justify-center transition-transform group-hover:scale-110">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                <circle cx="8" cy="12" r="5"/>
                <circle cx="16" cy="12" r="5"/>
              </svg>
            </div>
            <span className="text-xl font-bold text-gray-900">Lenskart</span>
          </div>
          <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-gray-600">
            {['Eyeglasses', 'Sunglasses', 'Contact Lenses', 'Stores'].map((item) => (
              <span key={item} className="relative hover:text-[#329c92] cursor-pointer transition-colors group">
                {item}
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-[#329c92] transition-all group-hover:w-full"></span>
              </span>
            ))}
          </nav>
          <button className="hidden sm:flex items-center gap-2 text-sm font-medium text-[#329c92] hover:bg-[#329c92]/5 px-4 py-2 rounded-lg transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Find Store
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <main className="pt-16 relative">
        <section className="min-h-[calc(100vh-4rem)] flex items-center py-12">
          <div className="max-w-7xl mx-auto px-6 w-full">
            <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
              {/* Left Content */}
              <div 
                className={`max-w-xl transition-all duration-1000 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}
              >
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-[#329c92]/10 rounded-full mb-6">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#329c92] opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-[#329c92]"></span>
                  </span>
                  <span className="text-[#329c92] text-sm font-semibold">India&apos;s #1 Eyewear Brand</span>
                </div>
                
                <h1 className="text-5xl lg:text-6xl xl:text-7xl font-light text-gray-900 leading-[1.1] mb-6">
                  See Better.
                  <br />
                  <span className="font-bold bg-gradient-to-r from-gray-900 via-[#329c92] to-gray-900 bg-clip-text text-transparent">
                    Look Better.
                  </span>
                </h1>
                
                <p className="text-gray-500 text-lg lg:text-xl leading-relaxed mb-8">
                  Premium eyewear with free home eye tests, virtual try-on, and doorstep delivery across India.
                </p>

                {/* Quick Features */}
                <div className="flex flex-wrap gap-4 mb-10">
                  {[
                    { icon: '🏠', text: 'Free Home Eye Test' },
                    { icon: '🔄', text: '14-Day Returns' },
                    { icon: '✨', text: 'Virtual Try-On' },
                  ].map((feature, i) => (
                    <div 
                      key={i} 
                      className="flex items-center gap-2 px-3 py-2 bg-gray-50 rounded-lg text-sm text-gray-600 hover:bg-gray-100 transition-colors cursor-default"
                      style={{ animationDelay: `${0.2 + i * 0.1}s` }}
                    >
                      <span>{feature.icon}</span>
                      <span>{feature.text}</span>
                    </div>
                  ))}
                </div>
                
                <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4">
                  <Button 
                    variant="primary" 
                    size="lg" 
                    onClick={onStartCall}
                    className="group relative bg-[#329c92] hover:bg-[#2a8a81] text-white px-8 py-4 text-base font-semibold rounded-xl transition-all hover:shadow-lg hover:shadow-[#329c92]/25 hover:-translate-y-0.5"
                  >
                    <span className="flex items-center gap-2">
                      {startButtonText}
                      <svg className="w-5 h-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </span>
                  </Button>
                  
                  <div className="flex items-center gap-3 text-sm text-gray-500">
                    <div className="flex -space-x-2">
                      {['👩', '👨', '👩‍🦰', '🧑'].map((emoji, i) => (
                        <div key={i} className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-sm border-2 border-white">
                          {emoji}
                        </div>
                      ))}
                    </div>
                    <span>Join <strong className="text-gray-700">{customerCount}M+</strong> happy customers</span>
                  </div>
                </div>
                
                <p className="text-gray-400 text-sm mt-6 flex items-center gap-2">
                  <svg className="w-4 h-4 text-[#329c92]" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10c0 3.866-3.582 7-8 7a8.841 8.841 0 01-4.083-.98L2 17l1.338-3.123C2.493 12.767 2 11.434 2 10c0-3.866 3.582-7 8-7s8 3.134 8 7zM7 9H5v2h2V9zm8 0h-2v2h2V9zM9 9h2v2H9V9z" clipRule="evenodd" />
                  </svg>
                  Talk to <span className="text-[#329c92] font-medium">Elena</span>, our AI assistant
                </p>
              </div>

              {/* Right Visual */}
              <div 
                className={`relative hidden lg:flex items-center justify-center transition-all duration-1000 delay-300 ${isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-8'}`}
              >
                <div className="relative">
                  {/* Pulsing ring behind glasses */}
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-64 h-64 rounded-full border-2 border-[#329c92]/20" style={{ animation: 'pulse-ring 3s ease-out infinite' }}></div>
                  </div>
                  
                  {/* Main Glasses SVG */}
                  <div className="relative z-10 p-8">
                    <svg viewBox="0 0 300 140" className="w-full max-w-lg text-gray-800 drop-shadow-xl">
                      <defs>
                        <linearGradient id="lensGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                          <stop offset="0%" stopColor="#329c92" stopOpacity="0.15"/>
                          <stop offset="100%" stopColor="#329c92" stopOpacity="0.05"/>
                        </linearGradient>
                        <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                          <feDropShadow dx="0" dy="4" stdDeviation="8" floodOpacity="0.1"/>
                        </filter>
                      </defs>
                      <g filter="url(#shadow)">
                        <ellipse cx="85" cy="70" rx="55" ry="45" fill="url(#lensGrad)" stroke="currentColor" strokeWidth="3"/>
                        <ellipse cx="215" cy="70" rx="55" ry="45" fill="url(#lensGrad)" stroke="currentColor" strokeWidth="3"/>
                        <path d="M140 70 Q150 50 160 70" stroke="currentColor" strokeWidth="3" fill="none"/>
                        <path d="M30 55 L5 48" stroke="currentColor" strokeWidth="3" strokeLinecap="round"/>
                        <path d="M270 55 L295 48" stroke="currentColor" strokeWidth="3" strokeLinecap="round"/>
                      </g>
                      {/* Shine effect */}
                      <ellipse cx="60" cy="55" rx="15" ry="8" fill="white" opacity="0.3"/>
                      <ellipse cx="190" cy="55" rx="15" ry="8" fill="white" opacity="0.3"/>
                    </svg>
                  </div>
                  
                  {/* Stats Card - Left */}
                  <div className="absolute -bottom-2 -left-8 bg-white shadow-xl rounded-2xl px-5 py-4 border border-gray-100 hover:scale-105 transition-transform cursor-default">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-[#329c92]/10 rounded-xl flex items-center justify-center">
                        <span className="text-xl">😊</span>
                      </div>
                      <div>
                        <p className="text-2xl font-bold text-gray-900">{customerCount}M+</p>
                        <p className="text-xs text-gray-500">Happy Customers</p>
                      </div>
                    </div>
                  </div>
                  
                  {/* Price Card - Top Right */}
                  <div className="absolute -top-2 -right-4 bg-white shadow-xl rounded-2xl px-5 py-4 border border-gray-100 hover:scale-105 transition-transform cursor-default">
                    <p className="text-xs text-gray-500 mb-1">Starting from</p>
                    <p className="text-3xl font-bold text-[#329c92]">₹999</p>
                    <p className="text-xs text-gray-400">Premium frames</p>
                  </div>
                  
                  {/* Rating Badge */}
                  <div className="absolute top-1/2 -right-16 transform -translate-y-1/2 bg-white shadow-lg rounded-xl px-4 py-3 border border-gray-100">
                    <div className="flex items-center gap-1 text-yellow-400 text-lg">
                      {'★★★★★'.split('').map((star, i) => <span key={i}>{star}</span>)}
                    </div>
                    <p className="text-xs text-gray-500 mt-1">4.8 rating</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Strip */}
        <section className="border-t border-gray-100 py-16 bg-gradient-to-b from-gray-50/80 to-white">
          <div className="max-w-7xl mx-auto px-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 lg:gap-12">
              {[
                { num: '5000+', label: 'Frame Styles', icon: '👓' },
                { num: `${storeCount}+`, label: 'Stores', icon: '🏪' },
                { num: `${cityCount}+`, label: 'Cities', icon: '🌆' },
                { num: '14 Days', label: 'Easy Returns', icon: '↩️' },
              ].map((item, i) => (
                <div 
                  key={i} 
                  className="text-center p-6 rounded-2xl hover:bg-white hover:shadow-lg transition-all cursor-default group"
                >
                  <span className="text-3xl mb-3 block group-hover:scale-110 transition-transform">{item.icon}</span>
                  <p className="text-3xl font-bold text-gray-900 mb-1">{item.num}</p>
                  <p className="text-sm text-gray-500">{item.label}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Trust Banner */}
        <section className="py-12 bg-[#329c92]">
          <div className="max-w-7xl mx-auto px-6">
            <div className="flex flex-col md:flex-row items-center justify-between gap-6">
              <div className="flex items-center gap-4 text-white">
                <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                  </svg>
                </div>
                <div>
                  <p className="font-semibold text-lg">100% Secure & Trusted</p>
                  <p className="text-white/80 text-sm">Safe payments • Quality assured</p>
                </div>
              </div>
              <div className="flex items-center gap-8 text-white/90 text-sm">
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Free Shipping
                </span>
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  COD Available
                </span>
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  EMI Options
                </span>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="py-8 bg-gray-50 border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 bg-[#329c92] rounded-md flex items-center justify-center">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                  <circle cx="8" cy="12" r="5"/>
                  <circle cx="16" cy="12" r="5"/>
                </svg>
              </div>
              <span className="font-semibold text-gray-700">Lenskart</span>
            </div>
            <p className="text-sm text-gray-400">© 2025 Lenskart. India&apos;s Largest Eyewear Brand.</p>
            <div className="flex items-center gap-6 text-sm text-gray-500">
              <span className="hover:text-[#329c92] cursor-pointer transition-colors">Privacy</span>
              <span className="hover:text-[#329c92] cursor-pointer transition-colors">Terms</span>
              <span className="hover:text-[#329c92] cursor-pointer transition-colors">Contact</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};
