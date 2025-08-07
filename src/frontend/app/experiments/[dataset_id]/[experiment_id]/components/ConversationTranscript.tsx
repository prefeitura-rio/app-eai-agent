'use client';

import React from 'react';
import { User, Bot } from 'lucide-react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { ConversationTurn } from '../../../types';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import ReasoningTimeline from './ReasoningTimeline';

interface ConversationTranscriptProps {
    transcript: ConversationTurn[] | null;
    defaultExpanded?: boolean;
}

const renderMarkdown = (content: string) => {
    marked.use({ breaks: true });
    const html = DOMPurify.sanitize(marked.parse(content) as string);
    return <div className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap" dangerouslySetInnerHTML={{ __html: html }} />;
};

export default function ConversationTranscript({ transcript, defaultExpanded = false }: ConversationTranscriptProps) {
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
                            {renderMarkdown(turn.user_message)}
                        </div>
                        <User className="h-6 w-6 flex-shrink-0" />
                    </div>

                    {/* Agent's Response */}
                    {turn.agent_message && (
                        <div className="flex items-start gap-3">
                            <Bot className="h-6 w-6 text-primary flex-shrink-0" />
                            <div className="max-w-[80%] rounded-lg bg-muted p-3 w-full">
                                {renderMarkdown(turn.agent_message)}
                                {turn.agent_reasoning_trace && turn.agent_reasoning_trace.length > 0 && (
                                    <div className="mt-4 pt-3 border-t border-muted/30">
                                        <Accordion type="single" collapsible className="w-full" value={defaultExpanded ? "reasoning" : undefined}>
                                            <AccordionItem value="reasoning" className="border-none">
                                                <AccordionTrigger className="text-xs p-2 hover:no-underline bg-muted/20 rounded-md">
                                                    <span className="font-medium text-primary">🔍 Ver Cadeia de Pensamento</span>
                                                </AccordionTrigger>
                                                <AccordionContent className="pt-2">
                                                    <ReasoningTimeline 
                                                        reasoningTrace={turn.agent_reasoning_trace} 
                                                        defaultExpanded={true}
                                                    />
                                                </AccordionContent>
                                            </AccordionItem>
                                        </Accordion>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}
