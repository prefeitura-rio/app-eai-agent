'use client';

import { API_BASE_URL } from '@/app/components/config';
import { HistoryItem } from '../components/VersionHistory';

// Interface para o payload de salvamento
interface SavePayload {
  agent_type: string;
  prompt_content: string;
  memory_blocks: any[];
  tools: string[];
  model_name: string | null;
  embedding_name: string | null;
  update_agents: boolean;
  author: string;
  reason: string;
}

// Função genérica para requisições API
async function apiRequest(url: string, options: RequestInit) {
  const res = await fetch(url, options);
  const result = await res.json();
  if (!res.ok) {
    throw new Error(result.detail || `HTTP error! status: ${res.status}`);
  }
  return result;
}

// Busca os detalhes de uma versão específica do histórico
export const fetchVersionDetails = async (version: HistoryItem, agentType: string, token: string) => {
  const url = `${API_BASE_URL}/api/v1/unified-history/version/${version.version_number}?agent_type=${agentType}`;
  return await apiRequest(url, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
};

// Salva as alterações do prompt e da configuração
export const saveChanges = async (payload: SavePayload, token: string) => {
  const url = `${API_BASE_URL}/api/v1/unified-save`;
  return await apiRequest(url, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
};

// Reseta o agente para a configuração padrão
export const resetAgent = async (agentType: string, updateAgents: boolean, token: string) => {
  const url = `${API_BASE_URL}/api/v1/unified-reset?agent_type=${agentType}&update_agents=${updateAgents}`;
  return await apiRequest(url, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
};
