'use client';

import React, { useState, useEffect, useCallback, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/app/contexts/AuthContext';
import { useHeader } from '@/app/contexts/HeaderContext';
import AgentSelector from './AgentSelector';
import PromptEditor from './PromptEditor';
import AgentConfiguration from './AgentConfiguration';
import VersionHistory, { HistoryItem } from './VersionHistory';
import ConfirmationModal from './ConfirmationModal';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { toast } from 'sonner';
import { Loader2, Save, RotateCcw, Settings, History } from 'lucide-react';
import { fetchVersionDetails, saveChanges, resetAgent } from '../services/api';

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

interface SettingsClientProps {
  agentTypes: string[];
  agentData: AgentData;
  selectedAgentType: string;
}

export default function SettingsClient({ agentTypes, agentData, selectedAgentType }: SettingsClientProps) {
  const { token } = useAuth();
  const router = useRouter();
  const { setTitle, setSubtitle, setPageActions } = useHeader();
  const [isPending, startTransition] = useTransition();
  

  // Estado dos campos do formulário
  const [selectedAgent, setSelectedAgent] = useState(selectedAgentType);
  const [promptContent, setPromptContent] = useState(agentData.prompt);
  const [clickUpCards, setClickUpCards] = useState(agentData.config.memory_blocks);
  const [tools, setTools] = useState(agentData.config.tools);
  const [modelName, setModelName] = useState(agentData.config.model_name);
  const [embeddingName, setEmbeddingName] = useState(agentData.config.embedding_name);
  const [updateAgents, setUpdateAgents] = useState(true);
  const [history, setHistory] = useState(agentData.history);
  
  // Estado da UI
  const [selectedVersionId, setSelectedVersionId] = useState<string | null>(null);
  const [isFetchingVersion, setIsFetchingVersion] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Estados dos Modais
  const [isSaveModalOpen, setSaveModalOpen] = useState(false);
  const [author, setAuthor] = useState('');
  const [reason, setReason] = useState('');
  const [isResetModalOpen, setResetModalOpen] = useState(false);
  const [resetConfirmationText, setResetConfirmationText] = useState('');

  // Configura o Header da página
  useEffect(() => {
    setTitle('Configurações EAI');
    setSubtitle('Gerencie os prompts e configurações dos agentes');
    setPageActions([
      { id: 'save', label: 'Salvar Alterações', icon: Save, onClick: () => handleOpenSaveModal(), variant: 'success', showLabel: true, className: 'w-48' },
      { id: 'reset', label: 'Resetar Tudo', icon: RotateCcw, onClick: () => { setResetConfirmationText(''); setResetModalOpen(true); }, variant: 'destructive', showLabel: true },
    ]);
    return () => setPageActions([]);
  }, [setTitle, setSubtitle, setPageActions]);

  const handleSelectVersion = useCallback(async (version: HistoryItem) => {
    if (!token) return;
    setIsFetchingVersion(true);
    setSelectedVersionId(version.version_id);
    try {
      const versionDetails = await fetchVersionDetails(version, selectedAgent, token);
      if (versionDetails.prompt) setPromptContent(versionDetails.prompt.content || '');
      if (versionDetails.config) {
        const config = versionDetails.config;
        setClickUpCards(JSON.stringify(config.memory_blocks || [], null, 2));
        setTools((config.tools || []).join(', '));
        setModelName(config.model_name || '');
        setEmbeddingName(config.embedding_name || '');
      }
    } catch  {
      toast.error("Erro ao buscar versão", { description: "Não foi possível carregar os dados da versão selecionada." });
    } finally {
      setIsFetchingVersion(false);
    }
  }, [token, selectedAgent]);

  // Sincroniza o estado do cliente com as props, reseta o estado 'dirty' e seleciona a versão ativa
  useEffect(() => {
    setSelectedAgent(selectedAgentType);
    setPromptContent(agentData.prompt);
    setClickUpCards(agentData.config.memory_blocks);
    setTools(agentData.config.tools);
    setModelName(agentData.config.model_name);
    setEmbeddingName(agentData.config.embedding_name);
    setHistory(agentData.history);
    setSelectedVersionId(null);

    // Encontra e seleciona a versão ativa ao carregar
    const activeVersion = agentData.history.find(h => h.is_active);
    if (activeVersion) {
      handleSelectVersion(activeVersion);
    }
  }, [agentData, selectedAgentType, handleSelectVersion]);


  const handleAgentChange = (newAgentType: string) => {
    startTransition(() => router.push(`/eai_settings?agent_type=${newAgentType}`));
  };

  const handleOpenSaveModal = () => {
    setAuthor('');
    setReason('');
    setSaveModalOpen(true);
  };

  const handleConfirmSave = async () => {
    if (!token) return;
    if (!author.trim() || !reason.trim()) {
      toast.error("Campos obrigatórios", { description: "Autor e motivo são obrigatórios." });
      return;
    }
    
    setIsSaving(true);
    try {
      const clickUpCardsArray = JSON.parse(clickUpCards);
      const payload = {
        agent_type: selectedAgent,
        prompt_content: promptContent,
        clickup_cards: clickUpCardsArray,
        tools: tools.split(',').map(t => t.trim()).filter(Boolean),
        model_name: modelName || null,
        embedding_name: embeddingName || null,
        update_agents: updateAgents,
        author,
        reason,
      };
      const result = await saveChanges(payload, token);
      toast.success("Sucesso!", { description: `Nova versão ${result.version_display} salva.` });
      setSaveModalOpen(false);
      window.location.reload();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
      toast.error("Erro ao Salvar", { description: errorMessage });
    } finally {
      setIsSaving(false);
    }
  };

  const handleConfirmReset = async () => {
    if (!token) return;
    setIsSaving(true);
    try {
      const result = await resetAgent(selectedAgent, updateAgents, token);
      toast.success("Sucesso!", { description: result.message || "Agente resetado com sucesso." });
      setResetModalOpen(false);
      router.refresh();
    } catch (error: unknown) {
      const errorMessage = error instanceof Error ? error.message : "An unknown error occurred";
      toast.error("Erro ao Resetar", { description: errorMessage });
    } finally {
      setIsSaving(false);
    }
  };

  const isLoading = isPending || isFetchingVersion;

  return (
    <>
      <ConfirmationModal
        open={isSaveModalOpen}
        onOpenChange={setSaveModalOpen}
        onConfirm={handleConfirmSave}
        title="Confirmar Alterações"
        description="Por favor, forneça o autor e o motivo para salvar esta nova versão."
        confirmText={isSaving ? "Salvando..." : "Salvar Versão"}
        confirmButtonVariant="success"
      >
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="author">
              Autor<span className="text-destructive">*</span>
            </Label>
            <Input id="author" value={author} onChange={(e) => setAuthor(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="reason">
              Motivo da Atualização<span className="text-destructive">*</span>
            </Label>
            <Input id="reason" value={reason} onChange={(e) => setReason(e.target.value)} />
          </div>
        </div>
      </ConfirmationModal>

      <ConfirmationModal
        open={isResetModalOpen}
        onOpenChange={setResetModalOpen}
        onConfirm={handleConfirmReset}
        title="Confirmar Reset"
        description={`Tem certeza que deseja resetar COMPLETAMENTE o agente '${selectedAgent}'? Esta ação removerá TODO o histórico e recriará as versões padrão. Esta ação NÃO pode ser desfeita.`}
        confirmText="Sim, resetar agente"
        confirmButtonVariant="destructive"
        confirmButtonDisabled={resetConfirmationText !== 'delete'}
      >
        <div className="space-y-4">
          <Label htmlFor="reset-confirmation">
            Para confirmar, digite <strong>delete</strong> abaixo:
          </Label>
          <Input 
            id="reset-confirmation" 
            value={resetConfirmationText} 
            onChange={(e) => setResetConfirmationText(e.target.value)}
            autoComplete="off"
          />
        </div>
      </ConfirmationModal>

      <div className="grid md:grid-cols-[1fr_420px] gap-6 h-full pb-6">
        <Card className="flex flex-col overflow-hidden">
          <CardHeader>
              <div className="flex items-center justify-between text-lg">
                  <CardTitle className="flex items-center gap-2">
                    <Settings className="h-5 w-5" />
                    <span>Configurações do Agente</span>
                  </CardTitle>
                  {isPending && <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />}
              </div>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto space-y-8 pt-4">
            <AgentSelector 
              agentTypes={agentTypes} 
              selectedAgent={selectedAgent} 
              onAgentChange={handleAgentChange} 
              updateAgents={updateAgents}
              onUpdateAgentsChange={setUpdateAgents}
              disabled={isLoading} 
            />
            <PromptEditor promptContent={promptContent} onPromptChange={setPromptContent} disabled={isLoading} />
            <AgentConfiguration
              clickUpCards={clickUpCards} onClickUpCardsChange={setClickUpCards}
              tools={tools} onToolsChange={setTools}
              modelName={modelName} onModelNameChange={setModelName}
              embeddingName={embeddingName} onEmbeddingNameChange={setEmbeddingName}
              updateAgents={updateAgents} onUpdateAgentsChange={setUpdateAgents}
              disabled={isLoading}
            />
          </CardContent>
        </Card>

        <Card className="flex flex-col overflow-hidden">
          <CardHeader>
              <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <History className="h-5 w-5" />
                    <span>Histórico de Versões</span>
                  </CardTitle>
                  {isFetchingVersion && <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />}
              </div>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto">
            <VersionHistory history={history} onSelectVersion={handleSelectVersion} selectedVersionId={selectedVersionId} disabled={isLoading} />
          </CardContent>
        </Card>
      </div>
    </>
  );
}