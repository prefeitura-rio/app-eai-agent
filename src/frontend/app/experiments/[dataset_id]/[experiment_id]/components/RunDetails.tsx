'use client';

import React from 'react';
import { Run } from '@/app/components/types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { User } from 'lucide-react';
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
                <CardHeader><CardTitle className="flex items-center gap-2"><User className="h-5 w-5" /> Mensagem do Usuário</CardTitle></CardHeader>
                <CardContent>
                    {run.input.mensagem_whatsapp_simulada || "Mensagem não disponível"}
                </CardContent>
            </Card>
            <Comparison run={run} />
            <Card>
                <CardHeader><CardTitle>Avaliações</CardTitle></CardHeader>
                <CardContent>
                    <Evaluations annotations={run.annotations} />
                </CardContent>
            </Card>
            <Card>
                <CardHeader><CardTitle>Cadeia de Pensamento (Reasoning)</CardTitle></CardHeader>
                <CardContent>
                    <ReasoningTimeline orderedSteps={run.output.agent_output?.ordered} />
                </CardContent>
            </Card>
        </div>
    );
}