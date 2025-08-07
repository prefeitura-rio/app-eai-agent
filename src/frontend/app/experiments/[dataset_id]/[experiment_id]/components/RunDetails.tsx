'use client';

import React, { useState, useMemo } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { ExperimentRun } from '../../../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { User, CheckSquare, Network, Trophy, Bot, MessageSquare, AlertTriangle, Brain } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import Comparison from './Comparison';
import Evaluations from './Evaluations';
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
    const [viewMode, setViewMode] = useState<'one_turn' | 'multi_turn'>('one_turn');
    
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

    const multiTurnReasoningTrace = useMemo(() => {
        if (isOneTurn || !run.multi_turn_analysis.transcript) {
            return [];
        }
        return run.multi_turn_analysis.transcript.flatMap(turn => turn.agent_reasoning_trace || []);
    }, [isOneTurn, run.multi_turn_analysis.transcript]);

    const reasoningTrace = isOneTurn 
        ? run.one_turn_analysis.agent_reasoning_trace 
        : multiTurnReasoningTrace;

    return (
        <div className="space-y-6">
            <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as 'one_turn' | 'multi_turn')} className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="one_turn">Análise de Turno Único</TabsTrigger>
                    <TabsTrigger value="multi_turn">Análise Multi-Turno</TabsTrigger>
                </TabsList>
            </Tabs>

            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-lg ">
                        <User className="h-5 w-5 text-primary" />
                        <span>Input do Usuário</span>
                    </CardTitle>
                </CardHeader>
                <CardContent className="pl-12">
                    {renderMarkdown(run.task_data.prompt || "Prompt não disponível")}
                </CardContent>
            </Card>
            
            {analysis.has_error ? (
                <ErrorDisplay message={analysis.error_message!} />
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
                                        {reasoningTrace && reasoningTrace.length > 0 && (
                                            <Dialog>
                                                <DialogTrigger asChild>
                                                    <Button variant="outline" size="sm">
                                                        <Brain className="h-4 w-4 mr-2" />
                                                        Ver Cadeia de Pensamento
                                                    </Button>
                                                </DialogTrigger>
                                                <DialogContent className="sm:max-w-[80vw] max-h-[80vh]">
                                                    <DialogHeader>
                                                        <DialogTitle>Cadeia de Pensamento</DialogTitle>
                                                    </DialogHeader>
                                                    <div className="overflow-y-auto max-h-[70vh]">
                                                        <ReasoningTimeline reasoningTrace={reasoningTrace} />
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
                                                {taskDataKeys.map(key => (
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
                            <CardTitle className="flex items-center gap-3 text-lg">
                                <CheckSquare className="h-5 w-5 text-primary" />
                                <span>Avaliações</span>
                            </CardTitle>
                        </CardHeader>
                        <CardContent>
                            <Evaluations key={viewMode} evaluations={analysis.evaluations} />
                        </CardContent>
                    </Card>
                    
                    <Accordion type="single" collapsible className="w-full">
                        <AccordionItem value="reasoning" className="border-none">
                            <AccordionTrigger className="hover:no-underline">
                                <div className="flex items-center gap-3">
                                    <Network className="h-5 w-5 text-primary" />
                                    <span>Cadeia de Pensamento</span>
                                </div>
                            </AccordionTrigger>
                            <AccordionContent>
                                {isOneTurn ? (
                                    <ReasoningTimeline reasoningTrace={run.one_turn_analysis.agent_reasoning_trace} />
                                ) : (
                                    <ReasoningTimeline reasoningTrace={multiTurnReasoningTrace} />
                                )}
                            </AccordionContent>
                        </AccordionItem>
                    </Accordion>
                </>
            )}
        </div>
    );
}
