export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // for LiveKit Cloud Sandbox
  sandboxId?: string;
  agentName?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Starbucks Voice Ordering',
  pageTitle: 'Starbucks Voice AI Barista - Order Coffee with Your Voice',
  pageDescription: 'Experience the future of coffee ordering with AI-powered voice technology',

  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#00704A',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#1E9668',
  startButtonText: 'Start Ordering Now',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};
