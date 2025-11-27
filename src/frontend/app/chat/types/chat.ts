import { ChatResponseData } from '../services/api';

export interface DisplayMessage {
  sender: 'user' | 'bot';
  content: string;
  fullResponse?: ChatResponseData;
  timestamp?: string;
  latency?: number;
  isTimeoutError?: boolean;
}

export interface InstrucaoItem {
  tema?: string;
  instrucoes?: string;
}
