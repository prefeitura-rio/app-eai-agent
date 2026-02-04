'use client';

import React, { useState, useMemo } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { ExperimentRun } from '../../../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { User, CheckSquare, Network, Trophy, Bot, MessageSquare, AlertTriangle, Brain, Search } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import Comparison from './Comparison';
import Evaluations, { useVisibleMetrics } from './Evaluations';
import MetricsSelector from './MetricsSelector';
import ReasoningTimeline from './ReasoningTimeline';
import ConversationTranscript from './ConversationTranscript';

interface RunDetailsProps {
  run: ExperimentRun;
}

const renderMarkdown = (content: string) => {
    marked.use({ breaks: true });
    const html = DOMPurify.sanitize(marked.parse(content) as string);
    return <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: html }} />;
};

const ErrorDisplay = ({ message }: { message: string }) => (
    <div className="flex items-center gap-3 text-destructive p-4 bg-destructive/10 rounded-lg">
        <AlertTriangle className="h-5 w-5" />
        <div className="text-sm">
            <p className="font-semibold">Erro na Geração da Resposta</p>
            <p className="text-destructive/80">{message}</p>
        </div>
    </div>
);

export default function RunDetails({ run }: RunDetailsProps) {
    // Determina o modo inicial baseado na disponibilidade dos dados
    const hasOneTurnData = useMemo(() => 
        run.one_turn_analysis && 
        run.one_turn_analysis.agent_message !== null,
        [run.one_turn_analysis]
    );
    
    const hasMultiTurnData = useMemo(() => 
        run.multi_turn_analysis && 
        run.multi_turn_analysis.final_agent_message !== null,
        [run.multi_turn_analysis]
    );
    
    const hasOneTurnError = useMemo(() => 
        run.one_turn_analysis && run.one_turn_analysis.has_error,
        [run.one_turn_analysis]
    );
    
    const hasMultiTurnError = useMemo(() => 
        run.multi_turn_analysis && run.multi_turn_analysis.has_error,
        [run.multi_turn_analysis]
    );
    
    const initialViewMode = useMemo(() => {
        // Se há erro em multi_turn, sempre começa com multi_turn para mostrar o erro
        if (run.multi_turn_analysis && run.multi_turn_analysis.has_error) {
            return 'multi_turn';
        }
        // Se há erro em one_turn, sempre começa com one_turn para mostrar o erro
        if (run.one_turn_analysis && run.one_turn_analysis.has_error) {
            return 'one_turn';
        }
        // Se há dados válidos em one_turn, começa com one_turn
        if (hasOneTurnData) {
            return 'one_turn';
        }
        // Caso contrário, começa com multi_turn
        return 'multi_turn';
    }, [hasOneTurnData, run.multi_turn_analysis, run.one_turn_analysis]);
    
    const [viewMode, setViewMode] = useState<'one_turn' | 'multi_turn'>(initialViewMode);
    
    const taskDataKeys = useMemo(() => 
        Object.keys(run.task_data).filter(key => key !== 'id' && key !== 'prompt'),
      [run.task_data]
    );

    // Estados separados para a seleção da coluna de referência em cada modo
    const [selectedGoldenKeyOneTurn, setSelectedGoldenKeyOneTurn] = useState<string>(
        taskDataKeys.includes('golden_response_one_shot') ? 'golden_response_one_shot' : taskDataKeys[0] || ''
    );
    const [selectedGoldenKeyMultiTurn, setSelectedGoldenKeyMultiTurn] = useState<string>(
        taskDataKeys.includes('golden_response_multiple_shot') ? 'golden_response_multiple_shot' : taskDataKeys[0] || ''
    );

    const isOneTurn = viewMode === 'one_turn';
    
    // Determina qual estado e setter usar com base no modo de visualização
    const selectedGoldenKey = isOneTurn ? selectedGoldenKeyOneTurn : selectedGoldenKeyMultiTurn;
    const setSelectedGoldenKey = isOneTurn ? setSelectedGoldenKeyOneTurn : setSelectedGoldenKeyMultiTurn;

    const analysis = isOneTurn ? run.one_turn_analysis : run.multi_turn_analysis;

    const agentResponse = isOneTurn 
        ? run.one_turn_analysis.agent_message 
        : run.multi_turn_analysis.final_agent_message;

    const goldenResponse = run.task_data[selectedGoldenKey] as string || "";

    const reasoningTrace = isOneTurn 
        ? run.one_turn_analysis.agent_reasoning_trace 
        : [];

    // Hook para gerenciar métricas visíveis
    const allMetrics = useMemo(() => 
        analysis.evaluations?.map(e => e.metric_name) || [], 
        [analysis.evaluations]
    );
    const { selectedMetrics, setSelectedMetrics } = useVisibleMetrics(allMetrics);

    // Verifica se deve exibir erro para o modo atual
    const shouldShowError = useMemo(() => {
        // Se há erro na análise atual, sempre mostra
        if (analysis.has_error) {
            return true;
        }
        
        // Se não há dados válidos para o modo atual
        if (isOneTurn && !hasOneTurnData) {
            return true;
        }
        
        if (!isOneTurn && !hasMultiTurnData) {
            return true;
        }
        
        return false;
    }, [analysis.has_error, isOneTurn, hasOneTurnData, hasMultiTurnData]);

    // Determina a mensagem de erro apropriada
    const errorMessage = useMemo(() => {
        // PRIORIDADE 1: Se há erro na análise atual, use essa mensagem
        if (analysis.has_error && analysis.error_message) {
            return analysis.error_message;
        }
        
        // PRIORIDADE 2: Se não há dados válidos para o modo atual
        if (isOneTurn && !hasOneTurnData) {
            return "Nenhuma resposta disponível para análise de turno único.";
        }
        
        if (!isOneTurn && !hasMultiTurnData) {
            return "Nenhuma resposta disponível para análise multi-turno.";
        }
        
        // PRIORIDADE 3: Fallback genérico
        return "Erro desconhecido na análise.";
    }, [analysis.has_error, analysis.error_message, isOneTurn, hasOneTurnData, hasMultiTurnData]);

    // Atualiza o viewMode se necessário - apenas quando os dados mudam E não há erro
    React.useEffect(() => {
        // Não muda o modo se há erro em qualquer análise
        if (hasOneTurnError || hasMultiTurnError) {
            return;
        }
        
        if (!hasOneTurnData && viewMode === 'one_turn') {
            setViewMode('multi_turn');
        } else if (!hasMultiTurnData && viewMode === 'multi_turn') {
            setViewMode('one_turn');
        }
    }, [hasOneTurnData, hasMultiTurnData, hasOneTurnError, hasMultiTurnError, viewMode]);

    return (
        <div className="space-y-6">
            {/* Mostra as abas apenas se ambos os modos têm dados OU se há erros em ambos */}
            {((hasOneTurnData && hasMultiTurnData) || (hasOneTurnError && hasMultiTurnError)) && (
                <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as 'one_turn' | 'multi_turn')} className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                        <TabsTrigger value="one_turn">Análise de Turno Único</TabsTrigger>
                        <TabsTrigger value="multi_turn">Análise Multi-Turno</TabsTrigger>
                    </TabsList>
                </Tabs>
            )}

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-lg ">
                        <User className="h-5 w-5 text-primary" />
                        <span>Input do Usuário</span>
                    </CardTitle>
                </CardHeader>
                <CardContent className="pl-12 prose-base-custom">
                    {renderMarkdown(run.task_data.prompt || "Prompt não disponível")}
                </CardContent>
            </Card>
            
            {/* Exibe erro se a análise atual tem erro ou não tem dados válidos */}
            {shouldShowError ? (
                <ErrorDisplay message={errorMessage} />
            ) : (
                <>
                    <div className="grid md:grid-cols-2 gap-6">
                        <Card>
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <CardTitle className="flex items-center gap-3 text-lg">
                                        <Bot className="h-5 w-5 text-primary" />
                                        <span>Resposta do Agente</span>
                                    </CardTitle>
                                    <div className="flex gap-2">
                                        {isOneTurn && reasoningTrace && reasoningTrace.length > 0 && (
                                            <Dialog>
                                                <DialogTrigger asChild>
                                                    <Button variant="outline" size="sm">
                                                        <Brain className="h-4 w-4 mr-2" />
                                                        Ver Detalhes
                                                    </Button>
                                                </DialogTrigger>
                                                <DialogContent className="sm:max-w-[80vw] max-h-[80vh]">
                                                    <DialogHeader>
                                                        <DialogTitle>Ver Detalhes</DialogTitle>
                                                    </DialogHeader>
                                                    <div className="overflow-y-auto max-h-[70vh]">
                                                        <ReasoningTimeline 
                                                            reasoningTrace={reasoningTrace} 
                                                            defaultExpanded={true}
                                                        />
                                                    </div>
                                                </DialogContent>
                                            </Dialog>
                                        )}
                                        {!isOneTurn && (
                                            <Dialog>
                                                <DialogTrigger asChild>
                                                    <Button variant="outline" size="sm" disabled={!run.multi_turn_analysis.transcript}>
                                                        <MessageSquare className="h-4 w-4 mr-2" />
                                                        Ver Transcrição
                                                    </Button>
                                                </DialogTrigger>
                                                <DialogContent className="sm:max-w-[60vw]">
                                                    <DialogHeader>
                                                        <DialogTitle>Transcrição da Conversa</DialogTitle>
                                                    </DialogHeader>
                                                    <div className="max-h-[70vh] overflow-y-auto p-4">
                                                        <ConversationTranscript transcript={run.multi_turn_analysis.transcript} />
                                                    </div>
                                                </DialogContent>
                                            </Dialog>
                                        )}
                                    </div>
                                </div>
                            </CardHeader>
                            <Comparison content={agentResponse || ''} />
                        </Card>

                        <Card>
                            <CardHeader>
                                <div className="flex items-center justify-between">
                                    <CardTitle className="flex items-center gap-3 text-lg">
                                        <Trophy className="h-5 w-5 text-primary" />
                                        <span>Resposta de Referência</span>
                                    </CardTitle>
                                    <div className="w-48">
                                        <Select value={selectedGoldenKey} onValueChange={setSelectedGoldenKey}>
                                            <SelectTrigger id="golden-key-selector" className="w-full">
                                                <SelectValue placeholder="Selecione a coluna..." />
                                            </SelectTrigger>
                                            <SelectContent>
                                                {taskDataKeys.map((key: string) => (
                                                    <SelectItem key={key} value={key}>{key}</SelectItem>
                                                ))}
                                            </SelectContent>
                                        </Select>
                                    </div>
                                </div>
                            </CardHeader>
                            <Comparison content={goldenResponse} />
                        </Card>
                    </div>
                    
                    <Card>
                        <CardHeader>
                            <div className="flex items-center justify-between">
                                <CardTitle className="flex items-center gap-3 text-lg">
                                    <CheckSquare className="h-5 w-5 text-primary" />
                                    <span>Avaliações</span>
                                </CardTitle>
                                <MetricsSelector
                                    availableMetrics={allMetrics}
                                    selectedMetrics={selectedMetrics}
                                    onSelectionChange={setSelectedMetrics}
                                    storageKey="evaluations-visible-metrics"
                                />
                            </div>
                        </CardHeader>
                        <CardContent>
                            <Evaluations key={viewMode} evaluations={analysis.evaluations} selectedMetrics={selectedMetrics} />
                        </CardContent>
                    </Card>
                    
                    <Card>
                        <CardHeader>
                            <CardTitle className="flex items-center gap-3 text-lg">
                                <Network className="h-5 w-5 text-primary" />
                                <span>Cadeia de Pensamento</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <Accordion type="single" collapsible className="w-full" defaultValue={undefined}>
                                <AccordionItem value="reasoning" className="border-none">
                                    <AccordionTrigger className="hover:no-underline">
                                        <div className="flex items-center gap-3">
                                            <Search className="h-4 w-4 text-blue-500" />
                                            <span className="text-blue-500">Ver Cadeia de Pensamento</span>
                                        </div>
                                    </AccordionTrigger>
                                    <AccordionContent>
                                        {isOneTurn ? (
                                            <ReasoningTimeline 
                                                reasoningTrace={run.one_turn_analysis.agent_reasoning_trace} 
                                                defaultExpanded={true}
                                            />
                                        ) : (
                                            <ConversationTranscript 
                                                transcript={run.multi_turn_analysis.transcript} 
                                                defaultExpanded={true}
                                            />
                                        )}
                                    </AccordionContent>
                                </AccordionItem>
                            </Accordion>
                        </CardContent>
                    </Card>
                </>
            )}
        </div>
    );
}
