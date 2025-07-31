'use client';

import React from 'react';
import { ExperimentRun } from '../../../types';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Lightbulb, Wrench, LogIn, MessageSquare, Bot } from 'lucide-react';

interface ReasoningTimelineProps {
  reasoningTrace: ExperimentRun['reasoning_trace'];
}

const getStepIcon = (messageType: string) => {
    switch (messageType) {
        case 'reasoning_message': return Lightbulb;
        case 'tool_call_message': return Wrench;
        case 'tool_return_message': return LogIn;
        case 'assistant_message': return Bot;
        default: return MessageSquare;
    }
};

const StepContent = ({ content }: { content: any }) => {
    if (typeof content === 'string') {
        return <p className="italic text-muted-foreground text-xs pl-6">{content}</p>;
    }
    if (typeof content === 'object' && content !== null) {
        return <pre className="p-4 bg-muted rounded-md text-xs whitespace-pre-wrap break-all font-mono text-foreground">{JSON.stringify(content, null, 2)}</pre>;
    }
    return null;
}

export default function ReasoningTimeline({ reasoningTrace }: ReasoningTimelineProps) {
    const trace = reasoningTrace.multi_turn || reasoningTrace.one_turn || [];

    if (!trace || trace.length === 0) {
        return <p className="text-sm text-muted-foreground">Nenhum passo de raciocínio disponível.</p>;
    }

    return (
        <Accordion type="multiple" className="w-full" defaultValue={trace.map((_, i) => `item-${i}`)}>
            {trace.map((step, index) => {
                const Icon = getStepIcon(step.message_type);
                const title = step.message_type ? step.message_type.replace(/_/g, ' ') : 'Passo Desconhecido';

                return (
                    <AccordionItem value={`item-${index}`} key={index}>
                        <AccordionTrigger className="hover:no-underline">
                            <div className="flex items-center gap-3">
                                <Icon className="h-5 w-5 text-primary" />
                                <span className="font-semibold text-left capitalize">{title}</span>
                            </div>
                        </AccordionTrigger>
                        <AccordionContent className="pl-12">
                            <StepContent content={step.content} />
                        </AccordionContent>
                    </AccordionItem>
                )
            })}
        </Accordion>
    );
}
