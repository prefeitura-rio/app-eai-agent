'use client';

import React from 'react';
import { User, Bot } from 'lucide-react';
import { ConversationTurn } from '../../../types';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import ReasoningTimeline from './ReasoningTimeline';

interface ConversationTranscriptProps {
    transcript: ConversationTurn[] | null;
}

export default function ConversationTranscript({ transcript }: ConversationTranscriptProps) {
    if (!transcript || transcript.length === 0) {
        return <p className="text-sm text-muted-foreground p-4">Nenhuma transcrição de conversa disponível.</p>;
    }

    return (
        <div className="space-y-4">
            {transcript.map((turn) => (
                <div key={turn.turn}>
                    {/* User's Message */}
                    <div className="flex items-start gap-3 justify-end mb-2">
                        <div className="max-w-[80%] rounded-lg bg-primary text-primary-foreground p-3">
                            <p className="text-sm">{turn.user_message}</p>
                        </div>
                        <User className="h-6 w-6 flex-shrink-0" />
                    </div>

                    {/* Agent's Response */}
                    {turn.agent_message && (
                        <div className="flex items-start gap-3">
                            <Bot className="h-6 w-6 text-primary flex-shrink-0" />
                            <div className="max-w-[80%] rounded-lg bg-muted p-3 w-full">
                                <p className="text-sm">{turn.agent_message}</p>
                                {turn.agent_reasoning_trace && turn.agent_reasoning_trace.length > 0 && (
                                    <Accordion type="single" collapsible className="w-full mt-2">
                                        <AccordionItem value="reasoning" className="border-none">
                                            <AccordionTrigger className="text-xs p-2 hover:no-underline">
                                                Ver Cadeia de Pensamento
                                            </AccordionTrigger>
                                            <AccordionContent>
                                                <ReasoningTimeline reasoningTrace={turn.agent_reasoning_trace} />
                                            </AccordionContent>
                                        </AccordionItem>
                                    </Accordion>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
