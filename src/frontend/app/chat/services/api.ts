'use client';

import { API_BASE_URL } from '@/app/components/config';

// --- Interfaces ---

interface ChatRequestPayload {
  user_number: string;
  message: string;
  // Add other optional agent parameters here if needed
}

interface ChatResponse {
  response: {
    data?: {
      messages: {
        content?: string;
        message_type: string;
      }[];
    };
  };
}

// --- API Function ---

export async function sendChatMessage(payload: ChatRequestPayload, token: string): Promise<string> {
  try {
    const res = await fetch(`${API_BASE_URL}/api/v1/eai-gateway/chat`, {
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

    const data: ChatResponse = await res.json();

    // Extract the assistant's final message from the response
    const assistantMessage = data.response?.data?.messages?.find(
      (msg) => msg.message_type === 'assistant_message' && msg.content
    );

    return assistantMessage?.content || "Não foi possível obter uma resposta do assistente.";

  } catch (error) {
    console.error("Error sending chat message:", error);
    const errorMessage = error instanceof Error ? error.message : "An unknown error occurred.";
    return `Erro: ${errorMessage}`;
  }
}
