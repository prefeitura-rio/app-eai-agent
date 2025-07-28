'use client';

import React from 'react';
import { marked } from 'marked';
import { Run, OrderedStep } from '@/app/components/types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Bot, Trophy } from 'lucide-react';

interface ComparisonProps {
  run: Run;
}

export default function Comparison({ run }: ComparisonProps) {
    const agentMessage = run.output.agent_output?.ordered?.find((m: OrderedStep) => m.type === "assistant_message");
    const agentAnswerHtml = agentMessage?.message?.content ? marked(agentMessage.message.content) : "<p class='text-muted-foreground italic'>Nenhuma resposta do agente disponível.</p>";
    const goldenAnswerHtml = run.reference_output.golden_answer ? marked(run.reference_output.golden_answer) : "<p class='text-muted-foreground italic'>Nenhuma resposta de referência disponível.</p>";

    return (
        <div className="grid md:grid-cols-2 gap-6">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-lg">
                        <Bot className="h-5 w-5 text-primary" />
                        <span>Resposta do Agente</span>
                    </CardTitle>
                </CardHeader>
                <CardContent className="prose text-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: agentAnswerHtml }} />
            </Card>
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-lg">
                        <Trophy className="h-5 w-5 text-primary" />
                        <span>Resposta de Referência (Golden)</span>
                    </CardTitle>
                </CardHeader>
                <CardContent className="prose text-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: goldenAnswerHtml }} />
            </Card>
        </div>
    );
}