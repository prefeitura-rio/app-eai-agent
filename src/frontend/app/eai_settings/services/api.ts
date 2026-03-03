'use client';

import { API_BASE_URL } from '@/app/components/config';
import { HistoryItem } from '../components/VersionHistory';

interface ClickUpCard {
  label: string;
  value: string;
  limit?: number;
}

// Interface para o payload de salvamento
interface SavePayload {
  agent_type: string;
  prompt_content: string;
  clickup_cards: ClickUpCard[];
  tools: string[];
  model_name: string | null;
  embedding_name: string | null;
  author: string;
  reason: string;
}

interface VersionDetails {
  prompt?: {
    content: string;
    metadata?: {
      prompt_tokens?: number | null;
      prompt_tokenizer?: string | null;
    };
  };
  config: {
    memory_blocks: ClickUpCard[];
    tools: string[];
    model_name: string;
    embedding_name: string;
  };
}

interface SaveResponse {
  success: boolean;
  unified_version_number: number;
  version_display: string;
  change_type: 'prompt' | 'config' | 'both';
  message: string;
  prompt_id?: string | null;
  config_id?: string | null;
  prompt_tokens?: number | null;
  prompt_tokenizer?: string | null;
}

interface ResetResponse {
  message: string;
}

interface DeleteVersionResponse {
  success: boolean;
  version_number: number;
  version_display?: string;
  active_version?: number;
  reactivated_version?: number;
  message: string;
}

interface UnifiedHistoryResponse {
  items: HistoryItem[];
}

// Função genérica para requisições API
async function apiRequest<T>(url: string, options: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    const errorResult = await res.json().catch(() => ({ detail: `HTTP error! status: ${res.status}` }));
    throw new Error(errorResult.detail || `HTTP error! status: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

// Busca os detalhes de uma versão específica do histórico
export const fetchVersionDetails = async (version: HistoryItem, agentType: string, token: string) => {
  const url = `${API_BASE_URL}/api/v1/unified-history/version/${version.version_number}?agent_type=${agentType}`;
  return await apiRequest<VersionDetails>(url, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
};

export const fetchUnifiedHistory = async (agentType: string, token: string) => {
  const url = `${API_BASE_URL}/api/v1/unified-history?agent_type=${agentType}&limit=50`;
  return await apiRequest<UnifiedHistoryResponse>(url, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
};

// Salva as alterações do prompt e da configuração
export const saveChanges = async (payload: SavePayload, token: string) => {
  const url = `${API_BASE_URL}/api/v1/unified-save`;
  return await apiRequest<SaveResponse>(url, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
};

// Reseta o agente para a configuração padrão
export const resetAgent = async (agentType: string, token: string) => {
  const url = `${API_BASE_URL}/api/v1/unified-reset?agent_type=${agentType}`;
  return await apiRequest<ResetResponse>(url, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
};

export const deleteVersion = async (agentType: string, versionNumber: number, token: string) => {
  const url = `${API_BASE_URL}/api/v1/unified-delete?agent_type=${encodeURIComponent(agentType)}&version_number=${versionNumber}`;
  return await apiRequest<DeleteVersionResponse>(url, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
