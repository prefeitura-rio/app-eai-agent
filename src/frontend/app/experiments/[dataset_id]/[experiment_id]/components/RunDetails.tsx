'use client';

import React, { useState, useMemo } from 'react';
import { ExperimentRun } from '../../../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { User, CheckSquare, Network, Trophy, Bot, MessageSquare } from 'lucide-react';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import Comparison from './Comparison';
import Evaluations from './Evaluations';
import ReasoningTimeline from './ReasoningTimeline';
import ConversationTranscript from './ConversationTranscript';

interface RunDetailsProps {
  run: ExperimentRun;
}

export default function RunDetails({ run }: RunDetailsProps) {
    const [viewMode, setViewMode] = useState<'one_turn' | 'multi_turn'>('one_turn');
    const taskDataKeys = useMemo(() => Object.keys(run.task_data), [run.task_data]);
    
    const [selectedGoldenKeyOneTurn, setSelectedGoldenKeyOneTurn] = useState<string>('golden_response');
    const [selectedGoldenKeyMultiTurn, setSelectedGoldenKeyMultiTurn] = useState<string>('golden_summary');

    const isOneTurn = viewMode === 'one_turn';
    const selectedGoldenKey = isOneTurn ? selectedGoldenKeyOneTurn : selectedGoldenKeyMultiTurn;
    const setSelectedGoldenKey = isOneTurn ? setSelectedGoldenKeyOneTurn : setSelectedGoldenKeyMultiTurn;

    const agentResponse = isOneTurn ? run.agent_response.one_turn : run.agent_response.multi_turn_final;
    const goldenResponse = run.task_data[selectedGoldenKey] as string || "";
    const reasoningTrace = isOneTurn ? run.reasoning_trace.one_turn : run.reasoning_trace.multi_turn;
    const evaluations = run.evaluations.filter(e => e.eval_type === (isOneTurn ? 'one' : 'multiple'));

    return (
        <div className="space-y-6">
            <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as any)} className="w-full">
                <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="one_turn">Single-Turn Analysis</TabsTrigger>
                    <TabsTrigger value="multi_turn">Multi-Turn Analysis</TabsTrigger>
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
                    <p className="text-foreground text-sm">{run.task_data.prompt || "Prompt não disponível"}</p>
                </CardContent>
            </Card>
            
            <div className="grid md:grid-cols-2 gap-6">
                <Card>
                    <CardHeader>
                        <div className="flex items-center justify-between">
                            <CardTitle className="flex items-center gap-3 text-lg">
                                <Bot className="h-5 w-5 text-primary" />
                                <span>Resposta do Agente</span>
                            </CardTitle>
                            {!isOneTurn && (
                                <Dialog>
                                    <DialogTrigger asChild>
                                        <Button variant="outline" size="sm">
                                            <MessageSquare className="h-4 w-4 mr-2" />
                                            Ver Transcrição
                                        </Button>
                                    </DialogTrigger>
                                    <DialogContent className="sm:max-w-[60vw]">
                                        <DialogHeader>
                                            <DialogTitle>Transcrição da Conversa</DialogTitle>
                                        </DialogHeader>
                                        <div className="max-h-[70vh] overflow-y-auto p-4">
                                            <ConversationTranscript transcript={run.reasoning_trace.multi_turn} />
                                        </div>
                                    </DialogContent>
                                </Dialog>
                            )}
                        </div>
                    </CardHeader>
                    <Comparison content={agentResponse!} />
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
                                    <SelectContent className="max-w-full">
                                        {taskDataKeys.map(key => (
                                            <SelectItem key={key} value={key} className="whitespace-normal">{key}</SelectItem>
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
                <CardContent className="pl-12">
                    <Evaluations evaluations={evaluations} />
                </CardContent>
            </Card>
            
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-lg">
                        <Network className="h-5 w-5 text-primary" />
                        <span>Cadeia de Pensamento</span>
                    </CardTitle>
                </CardHeader>
                <CardContent className="pl-12">
                    <ReasoningTimeline reasoningTrace={reasoningTrace} />
                </CardContent>
            </Card>
        </div>
    );
}
