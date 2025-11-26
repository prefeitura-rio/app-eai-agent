import { ChatResponseData } from '../services/api';

export interface DisplayMessage {
  sender: 'user' | 'bot';
  content: string;
  fullResponse?: ChatResponseData;
}

export interface InstrucaoItem {
  tema?: string;
  instrucoes?: string;
}
