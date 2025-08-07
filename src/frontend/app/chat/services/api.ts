'use client';

import { API_BASE_URL } from '@/app/components/config';

// --- Interfaces ---

export interface ChatRequestPayload {
  user_number: string;
  message: string;
  timeout?: number;
  polling_interval?: number;
  provider?: string;
}

export interface ToolCall {
  name: string;
  arguments: string;
  tool_call_id: string;
}

export interface ToolReturn {
  [key: string]: unknown;
}

export interface UsageStatistics {
  completion_tokens: number;
  prompt_tokens: number;
  total_tokens: number;
  step_count: number;
}

export interface AgentMessage {
  id: string;
  date: string;
  name: string | null;
  message_type: 'reasoning_message' | 'tool_call_message' | 'tool_return_message' | 'assistant_message';
  reasoning?: string;
  tool_call?: ToolCall;
  tool_return?: ToolReturn;
  content?: string;
}

export interface ChatResponseData {
  messages: AgentMessage[];
  usage: UsageStatistics;
}

interface ChatApiResponse {
  response: {
    data?: ChatResponseData;
  };
}

// --- API Function ---

export async function sendChatMessage(payload: ChatRequestPayload, token: string): Promise<ChatResponseData> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 300000); // 300 segundos (5 minutos)
    
    const res = await fetch(`${API_BASE_URL}/api/v1/eai-gateway/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    
    clearTimeout(timeoutId);

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Failed to parse error response.' }));
      throw new Error(errorData.detail || `Request failed with status ${res.status}`);
    }

    const data: ChatApiResponse = await res.json();

    if (!data.response?.data) {
      throw new Error("Resposta da API inválida: campo 'data' ausente.");
    }

    return data.response.data;

  } catch (error) {
    console.error("Error sending chat message:", error);
    
    let errorMessage = "An unknown error occurred.";
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        errorMessage = "Timeout: A requisição demorou mais de 5 minutos para responder.";
      } else {
        errorMessage = error.message;
      }
    }
    
    // Retornar um objeto de erro que corresponda à estrutura esperada
    return {
      messages: [{
        id: 'error',
        date: new Date().toISOString(),
        name: null,
        message_type: 'assistant_message',
        content: `Erro: ${errorMessage}`
      }],
      usage: { completion_tokens: 0, prompt_tokens: 0, total_tokens: 0, step_count: 0 }
    };
  }
}
