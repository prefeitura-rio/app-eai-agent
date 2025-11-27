import { ChatResponseData } from '../services/api';

export interface DisplayMessage {
  sender: 'user' | 'bot';
  content: string;
  fullResponse?: ChatResponseData;
  timestamp?: string;
  latency?: number;
}

export interface InstrucaoItem {
  tema?: string;
  instrucoes?: string;
}
