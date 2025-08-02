'use client';

import { API_BASE_URL } from '@/app/components/config';

// --- Interfaces ---

export interface AgentConfig {
  provider?: string;
  temperature?: number;
  model_name?: string;
  system_prompt?: string;
  history_limit?: number;
  embedding_limit?: number;
}

export interface ChatRequestPayload {
  user_id: string;
  prompt: string;
  agent_config: AgentConfig;
}

export interface LangGraphMessage {
    type: 'system' | 'context' | 'ai';
    data: {
        content: string;
        [key: string]: any;
    };
}

export type LangGraphChatResponse = LangGraphMessage[];


// --- API Function ---

export async function sendChatMessage(payload: ChatRequestPayload, token: string): Promise<LangGraphChatResponse> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/chat`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({ detail: 'Failed to parse error response.' }));
      throw new Error(errorData.detail || `Request failed with status ${res.status}`);
    }

    const data: LangGraphChatResponse = await res.json();

    if (!Array.isArray(data)) {
        throw new Error("Resposta da API inválida: não é um array.");
    }

    return data;

  } catch (error) {
    console.error("Error sending chat message:", error);
    const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
    return [
        {
            type: 'ai',
            data: {
                content: `Erro: ${errorMessage}`
            }
        }
    ];
  }
}
