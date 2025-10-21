'use client';

import React from 'react';
import { ReasoningStep } from '../../../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Lightbulb, Wrench, LogIn, MessageSquare, Bot, Brain } from 'lucide-react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

interface InstrucaoItem {
  tema?: string;
  instrucoes?: string;
}

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
                        {Boolean(obj.tool_return) && (
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
                                                } else if (obj.name === 'dharma_search_tool') {
                                                    // Special handling for dharma_search_tool
                                                    const toolReturn = obj.tool_return as {
                                                        id?: string;
                                                        created_at?: string;
                                                        updated_at?: string;
                                                        message?: string;
                                                        documents?: Array<{
                                                            title: string;
                                                            collection: string;
                                                            content: string;
                                                            id: string;
                                                            url: string;
                                                        }>;
                                                        metadata?: {
                                                            total_tokens?: number;
                                                        };
                                                    };
                                                    
                                                    return (
                                                        <div className="space-y-4">
                                                            {toolReturn.message && (
                                                                <div className="space-y-1">
                                                                    <h5 className="font-medium text-sm capitalize text-muted-foreground">Consulta</h5>
                                                                    <div className="pl-4">
                                                                        <div className="text-sm font-medium text-foreground">
                                                                            {toolReturn.message}
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            )}
                                                            {toolReturn.documents && Array.isArray(toolReturn.documents) && (
                                                                <div className="space-y-1">
                                                                    <h5 className="font-medium text-sm capitalize text-muted-foreground">Documentos Encontrados ({toolReturn.documents.length})</h5>
                                                                    <div className="pl-4 space-y-3">
                                                                        {toolReturn.documents.map((doc, index) => (
                                                                            <div key={doc.id || index} className="border border-border rounded-lg p-3 space-y-2">
                                                                                <div className="flex justify-between items-start">
                                                                                    <h6 className="font-medium text-sm text-foreground line-clamp-2">
                                                                                        {doc.title}
                                                                                    </h6>
                                                                                    {doc.collection && (
                                                                                        <span className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded-md ml-2 shrink-0">
                                                                                            {doc.collection}
                                                                                        </span>
                                                                                    )}
                                                                                </div>
                                                                                <div className="text-xs text-muted-foreground line-clamp-3">
                                                                                    {doc.content}
                                                                                </div>
                                                                                {doc.url && (
                                                                                    <a 
                                                                                        href={doc.url} 
                                                                                        target="_blank" 
                                                                                        rel="noopener noreferrer"
                                                                                        className="text-xs text-primary hover:underline inline-flex items-center gap-1"
                                                                                    >
                                                                                        Ver documento
                                                                                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                                                                        </svg>
                                                                                    </a>
                                                                                )}
                                                                            </div>
                                                                        ))}
                                                                    </div>
                                                                </div>
                                                            )}
                                                            {toolReturn.metadata?.total_tokens && (
                                                                <div className="space-y-1">
                                                                    <h5 className="font-medium text-sm capitalize text-muted-foreground">Metadata</h5>
                                                                    <div className="pl-4">
                                                                        <div className="text-xs text-muted-foreground">
                                                                            Tokens utilizados: {toolReturn.metadata.total_tokens}
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    );
                                                } else if (obj.name === 'equipments_instructions') {
                                                    // Special handling for equipments_instructions
                                                    const toolReturn = obj.tool_return as {
                                                        tema?: string;
                                                        next_tool_instructions?: string;
                                                        next_too_instructions?: string;
                                                        instrucoes?: Array<{
                                                            tema?: string;
                                                            instrucoes?: string;
                                                        }>;
                                                        categorias?: unknown;
                                                    };
                                                    
                                                    return (
                                                        <div className="space-y-4">
                                                            {(toolReturn.next_tool_instructions || toolReturn.next_too_instructions) && (
                                                                <div className="space-y-1">
                                                                    <h5 className="font-medium text-sm capitalize text-muted-foreground">Próximas Instruções</h5>
                                                                    <div className="pl-4">
                                                                        <div
                                                                            className="prose prose-sm dark:prose-invert max-w-none whitespace-pre-wrap"
                                                                            dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(marked.parse(toolReturn.next_tool_instructions || toolReturn.next_too_instructions || '') as string) }}
                                                                        />
                                                                    </div>
                                                                </div>
                                                            )}
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
                                                                        {toolReturn.instrucoes.map((item: InstrucaoItem, index: number) => (
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
                                                            {Boolean(toolReturn.categorias) && (
                                                                <div className="space-y-1">
                                                                    <h5 className="font-medium text-sm capitalize text-muted-foreground">Categorias</h5>
                                                                    <div className="pl-4">
                                                                        <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
                                                                            {JSON.stringify(toolReturn.categorias, null, 2)}
                                                                        </pre>
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
                        {Boolean(obj.arguments) && (
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

