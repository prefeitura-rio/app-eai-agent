'use client';

import React, { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
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

function SettingsPageContent() {
  const { token } = useAuth();
  const searchParams = useSearchParams();
  
  const [agentTypes, setAgentTypes] = useState<string[] | null>(null);
  const [agentData, setAgentData] = useState<AgentData | null>(null);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  // Efeito para buscar os tipos de agente (ocorre uma vez)
  useEffect(() => {
    if (token) {
      const getAgentTypes = async () => {
        try {
          const res = await fetch(`${API_BASE_URL}/api/v1/system-prompt/agent-types`, {
            headers: { 'Authorization': `Bearer ${token}` },
            cache: 'no-store',
          });
          if (!res.ok) throw new Error('Failed to fetch agent types');
          const data = await res.json();
          setAgentTypes(data.length > 0 ? data : ['agentic_search']);
        } catch (error) {
          console.error(error);
          setAgentTypes(['agentic_search']); // Fallback
        }
      };
      getAgentTypes();
    }
  }, [token]);

  // Efeito para determinar qual agente selecionar
  useEffect(() => {
    if (agentTypes) {
      const agentFromUrl = searchParams.get('agent_type');
      setSelectedAgent(agentFromUrl || agentTypes[0]);
    }
  }, [agentTypes, searchParams]);

  // Efeito para buscar os dados do agente selecionado
  useEffect(() => {
    if (selectedAgent && token) {
      const getAgentData = async () => {
        setAgentData(null); // Mostra o skeleton ao trocar de agente
        try {
          const [promptRes, configRes, historyRes] = await Promise.all([
            fetch(`${API_BASE_URL}/api/v1/system-prompt?agent_type=${selectedAgent}`, { headers: { 'Authorization': `Bearer ${token}` }, cache: 'no-store' }),
            fetch(`${API_BASE_URL}/api/v1/agent-config?agent_type=${selectedAgent}`, { headers: { 'Authorization': `Bearer ${token}` }, cache: 'no-store' }),
            fetch(`${API_BASE_URL}/api/v1/unified-history?agent_type=${selectedAgent}&limit=50`, { headers: { 'Authorization': `Bearer ${token}` }, cache: 'no-store' })
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
          console.error(`Failed to fetch data for agent ${selectedAgent}:`, error);
          setAgentData({ prompt: '', config: { memory_blocks: '[]', tools: '', model_name: '', embedding_name: '' }, history: [] });
        }
      };
      getAgentData();
    }
  }, [selectedAgent, token]);

  if (!agentTypes || !agentData) {
    return <SettingsSkeleton />;
  }

  return (
    <SettingsClient
      agentTypes={agentTypes}
      agentData={agentData}
      selectedAgentType={selectedAgent!}
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
