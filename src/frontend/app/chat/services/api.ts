'use client';

import { API_BASE_URL } from '@/app/components/config';

// --- Interfaces ---

export interface ChatRequestPayload {
  user_number: string;
  message: string;
  use_whatsapp_format: boolean;
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
  text?: string;
  message?: string;
  web_search_queries?: string[];
  sources?: unknown[];
  documents?: Array<{
    title: string;
    collection: string;
    content: string;
    id: string;
    url: string;
  }>;
  metadata?: {
    total_tokens?: number;
  };
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

// --- History Interfaces ---

export interface HistoryRequestPayload {
  user_id: string;
  session_timeout_seconds: number;
  use_whatsapp_format: boolean;
}

export interface HistoryMessage {
  id: string;
  date: string;
  session_id: string | null;
  time_since_last_message: number | null;
  name: string | null;
  message_type: 'user_message' | 'assistant_message' | 'tool_call_message' | 'tool_return_message' | 'reasoning_message' | 'usage_statistics';
  otid: string;
  sender_id: string | null;
  step_id: string;
  is_err: boolean | null;
  content?: string;
  tool_call?: ToolCall;
  tool_return?: ToolReturn;
  reasoning?: string;
  model_name?: string | null;
  finish_reason?: string | null;
  avg_logprobs?: number | null;
  usage_metadata?: Record<string, unknown>;
  // Campos específicos para tool_return_message
  status?: string;
  tool_call_id?: string;
  stdout?: unknown;
  stderr?: unknown;
  // Campos específicos para usage_statistics
  completion_tokens?: number;
  prompt_tokens?: number;
  total_tokens?: number;
  step_count?: number;
  steps_messages?: unknown;
  run_ids?: unknown;
  agent_id?: string;
  processed_at?: string;
  model_names?: string[];
}

export interface HistoryResponseData {
  data: HistoryMessage[];
}

// --- Delete History Interfaces ---

export interface DeleteHistoryRequestPayload {
  user_id: string;
}

export interface DeleteHistoryResponseData {
  thread_id: string;
  overall_result: string;
  tables: {
    checkpoints: {
      result: string;
      deleted_rows?: number;
      error?: string;
    };
    checkpoints_writes: {
      result: string;
      deleted_rows?: number;
      error?: string;
    };
  };
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

// --- History API Function ---

export async function getUserHistory(payload: HistoryRequestPayload, token: string): Promise<HistoryResponseData> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 segundos timeout
    
    const res = await fetch(`${API_BASE_URL}/api/v1/eai-gateway/history`, {
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

    const data: HistoryResponseData = await res.json();

    if (!data.data) {
      throw new Error("Resposta da API inválida: campo 'data' ausente.");
    }

    return data;

  } catch (error) {
    console.error("Error fetching user history:", error);
    
    let errorMessage = "An unknown error occurred.";
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        errorMessage = "Timeout: A requisição de histórico demorou mais de 30 segundos para responder.";
      } else {
        errorMessage = error.message;
      }
    }
    
    // Retornar estrutura vazia em caso de erro
    throw new Error(errorMessage);
  }
}

// --- Delete History API Function ---

export async function deleteUserHistory(payload: DeleteHistoryRequestPayload, token: string): Promise<DeleteHistoryResponseData> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30 segundos timeout
    
    const res = await fetch(`${API_BASE_URL}/api/v1/eai-gateway/history`, {
      method: 'DELETE',
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

    const data: DeleteHistoryResponseData = await res.json();

    if (!data.thread_id) {
      throw new Error("Resposta da API inválida: campo 'thread_id' ausente.");
    }

    return data;

  } catch (error) {
    console.error("Error deleting user history:", error);
    
    let errorMessage = "An unknown error occurred.";
    
    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        errorMessage = "Timeout: A requisição de exclusão demorou mais de 30 segundos para responder.";
      } else {
        errorMessage = error.message;
      }
    }
    
    throw new Error(errorMessage);
  }
}
