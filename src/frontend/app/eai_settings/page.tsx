'use client';

import React, { useState, useEffect, Suspense } from 'react';
import SettingsClient from './components/settings-client';
import SettingsSkeleton from './components/SettingsSkeleton';
import { API_BASE_URL } from '@/app/components/config';
import { useAuth } from '@/app/contexts/AuthContext';
import { HistoryItem } from './components/VersionHistory';

// Definindo a estrutura dos dados para clareza
interface AgentData {
  prompt: string;
  config: {
    memory_blocks: string;
    tools: string;
    model_name: string;
    embedding_name: string;
  };
  history: HistoryItem[];
}

const AGENT_TYPE = 'agentic_search';

function SettingsPageContent() {
  const { token } = useAuth();
  const [agentData, setAgentData] = useState<AgentData | null>(null);

  // Efeito para buscar os dados do agente selecionado
  useEffect(() => {
    if (token) {
      const getAgentData = async () => {
        setAgentData(null);
        try {
          const [promptRes, configRes, historyRes] = await Promise.all([
            fetch(`${API_BASE_URL}/api/v1/system-prompt?agent_type=${AGENT_TYPE}`, { headers: { 'Authorization': `Bearer ${token}` }, cache: 'no-store' }),
            fetch(`${API_BASE_URL}/api/v1/agent-config?agent_type=${AGENT_TYPE}`, { headers: { 'Authorization': `Bearer ${token}` }, cache: 'no-store' }),
            fetch(`${API_BASE_URL}/api/v1/unified-history?agent_type=${AGENT_TYPE}&limit=50`, { headers: { 'Authorization': `Bearer ${token}` }, cache: 'no-store' })
          ]);

          const promptData = promptRes.ok ? await promptRes.json() : { prompt: '' };
          const configData = configRes.ok ? await configRes.json() : { memory_blocks: [], tools: [], model_name: '', embedding_name: '' };
          const historyData = historyRes.ok ? await historyRes.json() : { items: [] };

          setAgentData({
            prompt: promptData.prompt || '',
            config: {
              memory_blocks: JSON.stringify(configData.memory_blocks || [], null, 2),
              tools: (configData.tools || []).join(', '),
              model_name: configData.model_name || '',
              embedding_name: configData.embedding_name || '',
            },
            history: historyData.items || [],
          });
        } catch (error) {
          console.error(`Failed to fetch data for agent ${AGENT_TYPE}:`, error);
          setAgentData({ prompt: '', config: { memory_blocks: '[]', tools: '', model_name: '', embedding_name: '' }, history: [] });
        }
      };
      getAgentData();
    }
  }, [token]);

  if (!agentData) {
    return <SettingsSkeleton />;
  }

  return (
    <SettingsClient
      agentData={agentData}
      selectedAgentType={AGENT_TYPE}
    />
  );
}


export default function SettingsPage() {
  return (
    <Suspense fallback={<SettingsSkeleton />}>
      <SettingsPageContent />
    </Suspense>
  );
}
