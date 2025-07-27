'use client';

import React from 'react';
import { marked } from 'marked';
import { OrderedStep } from '@/app/components/types';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Lightbulb, Wrench, LogIn, MessageSquare, BarChart } from 'lucide-react';

interface ReasoningTimelineProps {
  orderedSteps: OrderedStep[];
}

export default function ReasoningTimeline({ orderedSteps }: ReasoningTimelineProps) {
    if (!orderedSteps || orderedSteps.length === 0) {
        return <p className="text-sm text-muted-foreground">Nenhum passo de raciocínio disponível.</p>;
    }

    let sequenceCounter = 0;
    let currentStepPrefix = "";

    const getIcon = (stepType: string) => {
        switch (stepType) {
            case "reasoning_message": return Lightbulb;
            case "tool_call_message": return Wrench;
            case "tool_return_message": return LogIn;
            case "assistant_message": return MessageSquare;
            case "letta_usage_statistics": return BarChart;
            default: return Lightbulb;
        }
    };

    const defaultValues = orderedSteps.map((_, index) => `item-${index}`);

    return (
        <Accordion type="multiple" className="w-full" defaultValue={defaultValues}>
            {orderedSteps.map((step, index) => {
                let title: string = "";
                let content: React.ReactNode = null;
                const Icon = getIcon(step.type);

                switch (step.type) {
                    case "reasoning_message":
                        sequenceCounter++;
                        currentStepPrefix = `${sequenceCounter}. `;
                        title = `${currentStepPrefix}Raciocínio`;
                        content = <p className="mb-0 italic text-muted-foreground" dangerouslySetInnerHTML={{ __html: `"${step.message.reasoning}"` }} />;
                        break;
                    case "tool_call_message":
                        title = `${currentStepPrefix}Chamada de Ferramenta: ${step.message.tool_call.name}`;
                        content = <pre className="p-4 bg-muted rounded-md text-xs whitespace-pre-wrap font-mono text-foreground">{JSON.stringify(step.message.tool_call.arguments, null, 2)}</pre>;
                        break;
                    case "tool_return_message":
                        title = `${currentStepPrefix}Retorno da Ferramenta: ${step.message.name}`;
                        content = (
                            <div className="space-y-4">
                                {step.message.tool_return.text && (
                                    <div className="prose prose-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: marked(step.message.tool_return.text) }} />
                                )}
                                {step.message.tool_return.web_search_queries && (
                                    <div>
                                        <hr className="my-2 border-dashed" />
                                        <h4 className="font-semibold text-xs">Web Search Queries:</h4>
                                        <pre className="p-2 bg-muted rounded-md text-xs whitespace-pre-wrap font-mono text-foreground">{JSON.stringify(step.message.tool_return.web_search_queries, null, 2)}</pre>
                                    </div>
                                )}
                                {step.message.tool_return.sources && (
                                    <div>
                                        <hr className="my-2 border-dashed" />
                                        <Accordion type="single" collapsible>
                                            <AccordionItem value="sources">
                                                <AccordionTrigger className="text-xs font-semibold">Sources</AccordionTrigger>
                                                <AccordionContent>
                                                    <pre className="p-2 bg-muted rounded-md text-xs whitespace-pre-wrap font-mono text-foreground">{JSON.stringify(step.message.tool_return.sources, null, 2)}</pre>
                                                </AccordionContent>
                                            </AccordionItem>
                                        </Accordion>
                                    </div>
                                )}
                            </div>
                        );
                        break;
                    case "assistant_message":
                        sequenceCounter++;
                        currentStepPrefix = `${sequenceCounter}. `;
                        title = `Mensagem do Assistente`;
                        content = <div className="prose prose-sm dark:prose-invert max-w-none" dangerouslySetInnerHTML={{ __html: marked(step.message.content) }} />;
                        break;
                    case "letta_usage_statistics":
                        title = "Estatísticas de Uso";
                        content = (
                            <div className="text-sm grid grid-cols-3 gap-2">
                                <p><strong>Tokens Totais:</strong> {step.message.total_tokens}</p>
                                <p><strong>Tokens de Prompt:</strong> {step.message.prompt_tokens}</p>
                                <p><strong>Tokens de Conclusão:</strong> {step.message.completion_tokens}</p>
                            </div>
                        );
                        break;
                    default:
                        return null;
                }

                return (
                    <AccordionItem value={`item-${index}`} key={index}>
                        <AccordionTrigger className="hover:no-underline">
                            <div className="flex items-center gap-3">
                                <Icon className="h-5 w-5 text-primary" />
                                <span className="font-semibold text-left">{title}</span>
                            </div>
                        </AccordionTrigger>
                        <AccordionContent className="pl-12">
                            {content}
                        </AccordionContent>
                    </AccordionItem>
                );
            })}
        </Accordion>
    );
}