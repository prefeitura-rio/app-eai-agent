'use client';

import React from 'react';
import { Run } from '@/app/components/types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { User, CheckSquare, Network } from 'lucide-react';
import Comparison from './Comparison';
import Evaluations from './Evaluations';
import ReasoningTimeline from './ReasoningTimeline';

interface RunDetailsProps {
  run: Run;
}

export default function RunDetails({ run }: RunDetailsProps) {
    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-lg ">
                        <User className="h-5 w-5 text-primary" />
                        <span>Mensagem do Usuário</span>
                    </CardTitle>
                </CardHeader>
                <CardContent className="pl-12">
                    <p className="text-foreground text-sm">{run.input.mensagem_whatsapp_simulada || "Mensagem não disponível"}</p>
                </CardContent>
            </Card>
            
            <Comparison run={run} />
            
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-lg">
                        <CheckSquare className="h-5 w-5 text-primary" />
                        <span>Avaliações</span>
                    </CardTitle>
                </CardHeader>
                <CardContent className="pl-12">
                    <Evaluations annotations={run.annotations} />
                </CardContent>
            </Card>
            
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-lg">
                        <Network className="h-5 w-5 text-primary" />
                        <span>Cadeia de Pensamento (Reasoning)</span>
                    </CardTitle>
                </CardHeader>
                <CardContent className="pl-12">
                    <ReasoningTimeline orderedSteps={run.output.agent_output?.ordered} />
                </CardContent>
            </Card>
        </div>
    );
}