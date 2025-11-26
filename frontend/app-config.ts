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
  companyName: 'Lenskart',
  pageTitle: 'Lenskart Voice Assistant',
  pageDescription: 'Your Lenskart Sales Assistant - Eyewear, Franchise & Corporate Solutions',

  supportsChatInput: true,
  supportsVideoInput: true,
  supportsScreenShare: true,
  isPreConnectBufferEnabled: true,

  logo: '/lenskart-logo.svg',
  accent: '#11dacc',
  logoDark: '/lenskart-logo-dark.svg',
  accentDark: '#11dacc',
  startButtonText: 'Start Conversation',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};
