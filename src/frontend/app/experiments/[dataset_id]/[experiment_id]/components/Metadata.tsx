'use client';

import React from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { ExperimentDetails } from '../../../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Settings, Bot, Scale } from 'lucide-react';

interface MetadataProps {
  metadata: ExperimentDetails['experiment_metadata'];
}

const MarkdownRenderer = ({ content }: { content: string }) => {
    marked.use({ breaks: true });
    const html = DOMPurify.sanitize(marked.parse(content) as string);
    return (
        <div
            className="prose prose-sm dark:prose-invert max-w-none p-4 bg-muted rounded-md"
            dangerouslySetInnerHTML={{ __html: html }}
        />
    );
};

export default function Metadata({ metadata }: MetadataProps) {
    if (!metadata) return null;

    const { agent_config, judge_model, judges_prompts } = metadata;

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-3 text-lg">
                    <Settings className="h-5 w-5 text-primary" />
                    <span>Parâmetros do Experimento</span>
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                    <div>
                        <p className="font-semibold flex items-center gap-2"><Bot className="h-4 w-4" /> Modelo do Agente:</p>
                        <p className="text-muted-foreground pl-6">{agent_config?.model || "N/A"}</p>
                    </div>
                    <div>
                        <p className="font-semibold flex items-center gap-2"><Scale className="h-4 w-4" /> Modelo do Juiz:</p>
                        <p className="text-muted-foreground pl-6">{judge_model || "N/A"}</p>
                    </div>
                    <div>
                        <p className="font-semibold">Ferramentas do Agente:</p>
                        <p className="text-muted-foreground">{agent_config?.tools?.join(", ") || "Nenhuma"}</p>
                    </div>
                </div>

                <Accordion type="multiple" className="w-full space-y-2">
                    {agent_config?.system && (
                        <AccordionItem value="system-prompt">
                            <AccordionTrigger>System Prompt do Agente</AccordionTrigger>
                            <AccordionContent className="overflow-visible">
                                <MarkdownRenderer content={agent_config.system} />
                            </AccordionContent>
                        </AccordionItem>
                    )}
                    {judges_prompts && (
                        <AccordionItem value="judge-prompts">
                            <AccordionTrigger>Prompts do Juiz</AccordionTrigger>
                            <AccordionContent className="overflow-visible">
                                <Tabs defaultValue={Object.keys(judges_prompts)[0]} className="w-full">
                                    <TabsList>
                                        {Object.keys(judges_prompts).map(key => (
                                            <TabsTrigger key={key} value={key} className="text-xs">{key.replace(/_/g, ' ')}</TabsTrigger>
                                        ))}
                                    </TabsList>
                                    {Object.entries(judges_prompts).map(([key, value]) => (
                                        <TabsContent key={key} value={key}>
                                            <MarkdownRenderer content={String(value)} />
                                        </TabsContent>
                                    ))}
                                </Tabs>
                            </AccordionContent>
                        </AccordionItem>
                    )}
                </Accordion>
            </CardContent>
        </Card>
    );
}
