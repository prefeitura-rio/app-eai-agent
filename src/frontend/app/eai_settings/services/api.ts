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
  update_agents: boolean;
  author: string;
  reason: string;
}

interface VersionDetails {
  prompt: { content: string };
  config: {
    memory_blocks: ClickUpCard[];
    tools: string[];
    model_name: string;
    embedding_name: string;
  };
}

interface SaveResponse {
  version_display: string;
}

interface ResetResponse {
  message: string;
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
export const resetAgent = async (agentType: string, updateAgents: boolean, token: string) => {
  const url = `${API_BASE_URL}/api/v1/unified-reset?agent_type=${agentType}&update_agents=${updateAgents}`;
  return await apiRequest<ResetResponse>(url, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
