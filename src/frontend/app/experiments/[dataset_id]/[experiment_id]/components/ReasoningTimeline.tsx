'use client';

import React from 'react';
import { ReasoningStep } from '../../../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Lightbulb, Wrench, LogIn, MessageSquare, Bot, Brain } from 'lucide-react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

interface ReasoningTimelineProps {
  reasoningTrace: ReasoningStep[] | null;
  defaultExpanded?: boolean;
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

const renderContent = (content: unknown, messageType: string): React.ReactNode => {
    // Render based on message type
    switch (messageType) {
        case 'assistant_message':
        case 'reasoning_message':
        case 'hidden_reasoning_message':
        case 'system_message':
        case 'user_message':
            // These should be rendered as markdown
            if (typeof content === 'string') {
                marked.use({ breaks: true });
                const html = DOMPurify.sanitize(marked.parse(content) as string);
                return (
                    <div
                        className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap"
                        dangerouslySetInnerHTML={{ __html: html }}
                    />
                );
            }
            break;
            
        case 'tool_return_message':
            // This is an object with name and tool_return
            if (typeof content === 'object' && content !== null) {
                const obj = content as { name?: string; tool_return?: unknown };
                return (
                    <div className="space-y-3">
                        {obj.name && (
                            <div className="space-y-1">
                                <h4 className="font-semibold text-sm capitalize text-muted-foreground">Tool Name</h4>
                                <div className="pl-4">
                                    <p className="text-sm">{obj.name}</p>
                                </div>
                            </div>
                        )}
                        {obj.tool_return && (
                            <div className="space-y-1">
                                <h4 className="font-semibold text-sm capitalize text-muted-foreground">Tool Return</h4>
                                <div className="pl-4">
                                    {typeof obj.tool_return === 'string' ? (
                                        <div
                                            className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap"
                                            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(obj.tool_return) as string) }}
                                        />
                                    ) : typeof obj.tool_return === 'object' && obj.tool_return !== null ? (
                                        // Handle nested objects - go one level deep
                                        <div className="space-y-2">
                                            {(() => {
                                                const entries = Object.entries(obj.tool_return);
                                                
                                                // If it's google_search, order the fields specifically
                                                if (obj.name === 'google_search') {
                                                    const orderedFields = ['text', 'web_search_queries', 'sources', 'id'];
                                                    const orderedEntries = [];
                                                    
                                                    // Add fields in the specified order
                                                    for (const field of orderedFields) {
                                                        const entry = entries.find(([key]) => key === field);
                                                        if (entry) {
                                                            orderedEntries.push(entry);
                                                        }
                                                    }
                                                    
                                                    // Add any remaining fields
                                                    for (const entry of entries) {
                                                        if (!orderedFields.includes(entry[0])) {
                                                            orderedEntries.push(entry);
                                                        }
                                                    }
                                                    
                                                    return orderedEntries.map(([key, value]) => (
                                                        <div key={key} className="space-y-1">
                                                            <h5 className="font-medium text-xs capitalize text-muted-foreground">{key.replace(/_/g, ' ')}</h5>
                                                            <div className="pl-4">
                                                                {key === 'sources' ? (
                                                                    <Accordion type="single" collapsible className="w-full">
                                                                        <AccordionItem value="sources" className="border-none">
                                                                            <AccordionTrigger className="text-xs p-2 hover:no-underline">
                                                                                Ver Fontes
                                                                            </AccordionTrigger>
                                                                            <AccordionContent>
                                                                                {typeof value === 'string' ? (
                                                                                    <div
                                                                                        className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap"
                                                                                        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(value) as string) }}
                                                                                    />
                                                                                ) : (
                                                                                    <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
                                                                                        {JSON.stringify(value, null, 2)}
                                                                                    </pre>
                                                                                )}
                                                                            </AccordionContent>
                                                                        </AccordionItem>
                                                                    </Accordion>
                                                                ) : typeof value === 'string' ? (
                                                                    <div
                                                                        className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap"
                                                                        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(value) as string) }}
                                                                    />
                                                                ) : (
                                                                    <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
                                                                        {JSON.stringify(value, null, 2)}
                                                                    </pre>
                                                                )}
                                                            </div>
                                                        </div>
                                                    ));
                                                } else if (obj.name === 'equipments_instructions') {
                                                    // Special handling for equipments_instructions
                                                    const toolReturn = obj.tool_return as {
                                                        tema?: string;
                                                        instrucoes?: Array<{
                                                            tema?: string;
                                                            instrucoes?: string;
                                                        }>;
                                                    };
                                                    
                                                    return (
                                                        <div className="space-y-4">
                                                            {toolReturn.tema && (
                                                                <div className="space-y-1">
                                                                    <h5 className="font-medium text-sm capitalize text-muted-foreground">Tema</h5>
                                                                    <div className="pl-4">
                                                                        <div className="text-sm font-medium text-foreground">
                                                                            {toolReturn.tema}
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            )}
                                                            {toolReturn.instrucoes && Array.isArray(toolReturn.instrucoes) && (
                                                                <div className="space-y-1">
                                                                    <h5 className="font-medium text-sm capitalize text-muted-foreground">Instruções</h5>
                                                                    <div className="pl-4 space-y-3">
                                                                        {toolReturn.instrucoes.map((item: any, index: number) => (
                                                                            <div key={index} className="border-l-2 border-primary/20 pl-3">
                                                                                {/* Renderiza tema primeiro se existir */}
                                                                                {item.tema && (
                                                                                    <div className="text-xs text-muted-foreground mb-2">
                                                                                        <span className="font-medium">Tema:</span> {item.tema}
                                                                                    </div>
                                                                                )}
                                                                                {/* Renderiza instruções se existir */}
                                                                                {item.instrucoes && typeof item.instrucoes === 'string' && (
                                                                                    <div
                                                                                        className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap"
                                                                                        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(item.instrucoes) as string) }}
                                                                                    />
                                                                                )}
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    );
                                                } else {
                                                    // Default behavior for other tools
                                                    return entries.map(([key, value]) => (
                                                        <div key={key} className="space-y-1">
                                                            <h5 className="font-medium text-xs capitalize text-muted-foreground">{key.replace(/_/g, ' ')}</h5>
                                                            <div className="pl-4">
                                                                {typeof value === 'string' ? (
                                                                    <div
                                                                        className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap"
                                                                        dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(value) as string) }}
                                                                    />
                                                                ) : (
                                                                    <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
                                                                        {JSON.stringify(value, null, 2)}
                                                                    </pre>
                                                                )}
                                                            </div>
                                                        </div>
                                                    ));
                                                }
                                            })()}
                                        </div>
                                    ) : (
                                        <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
                                            {JSON.stringify(obj.tool_return, null, 2)}
                                        </pre>
                                    )}
                                </div>
                            </div>
                        )}
                    </div>
                );
            }
            return null;
            
        case 'tool_call_message':
            // This is an object with name and arguments
            if (typeof content === 'object' && content !== null) {
                const obj = content as { name?: string; arguments?: unknown };
                return (
                    <div className="space-y-3">
                        {obj.name && (
                            <div className="space-y-1">
                                <h4 className="font-semibold text-sm capitalize text-muted-foreground">Tool Name</h4>
                                <div className="pl-4">
                                    <p className="text-sm">{obj.name}</p>
                                </div>
                            </div>
                        )}
                        {obj.arguments && (
                            <div className="space-y-1">
                                <h4 className="font-semibold text-sm capitalize text-muted-foreground">Arguments</h4>
                                <div className="pl-4">
                                    <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
                                        {JSON.stringify(obj.arguments, null, 2)}
                                    </pre>
                                </div>
                            </div>
                        )}
                    </div>
                );
            }
            return null;
            
        case 'usage_statistics':
            // This is an object with usage statistics - render directly as JSON
            if (typeof content === 'object' && content !== null) {
                return (
                    <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
                        {JSON.stringify(content, null, 2)}
                    </pre>
                );
            }
            return null;
    }
    
    // Fallback for unknown types
    if (typeof content === 'string') {
        return <p className="text-sm">{content}</p>;
    }
    
    return (
        <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
            {JSON.stringify(content, null, 2)}
        </pre>
    );
};

const StepContent = ({ content, messageType }: { content: unknown; messageType: string }) => {
    return (
        <div className="p-4 bg-muted/50 border rounded-md">
            {renderContent(content, messageType)}
        </div>
    );
};

export default function ReasoningTimeline({ reasoningTrace, defaultExpanded = false }: ReasoningTimelineProps) {
    if (!reasoningTrace || reasoningTrace.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-lg">
                        <Brain className="h-5 w-5 text-primary" />
                        <span>Cadeia de Pensamento</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground p-4">Nenhum passo de raciocínio disponível.</p>
                </CardContent>
            </Card>
        );
    }

    // Se defaultExpanded é true, todos os itens começam expandidos
    const defaultValue = defaultExpanded 
        ? reasoningTrace.map((_, i) => `item-${i}`)
        : [];

    return (
        <Accordion type="multiple" className="w-full" defaultValue={defaultValue}>
            {reasoningTrace.map((step, index) => {
                const Icon = getStepIcon(step.message_type);
                const title = step.message_type.replace(/_/g, ' ');

                return (
                    <AccordionItem value={`item-${index}`} key={index}>
                        <AccordionTrigger className="hover:no-underline">
                            <div className="flex items-center gap-3">
                                <Icon className="h-5 w-5 text-primary" />
                                <span className="font-semibold text-left capitalize">{title}</span>
                            </div>
                        </AccordionTrigger>
                        <AccordionContent>
                            <StepContent content={step.content} messageType={step.message_type} />
                        </AccordionContent>
                    </AccordionItem>
                )
            })}
        </Accordion>
    );
};

