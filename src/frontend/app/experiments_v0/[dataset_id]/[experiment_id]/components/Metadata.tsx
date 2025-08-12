'use client';

import React from 'react';
import { ExperimentMetadata } from '@/app/components/types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Settings } from 'lucide-react';

interface MetadataProps {
  metadata: ExperimentMetadata | null;
}

const PromptSection = ({ title, content, collapseId }: { title: string, content: string | undefined, collapseId: string }) => {
    if (!content) return null;
    return (
        <div className="col-span-full mt-2">
            <Accordion type="single" collapsible>
                <AccordionItem value={collapseId}>
                    <AccordionTrigger className="text-sm font-semibold">{title}</AccordionTrigger>
                    <AccordionContent>
                        <pre className="p-4 bg-muted text-foreground rounded-md text-xs whitespace-pre-wrap">{content}</pre>
                    </AccordionContent>
                </AccordionItem>
            </Accordion>
        </div>
    );
};

export default function Metadata({ metadata }: MetadataProps) {
    if (!metadata) return null;

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-3 text-lg">
                    <Settings className="h-5 w-5 text-primary" />
                    <span>Parâmetros do Experimento</span>
                </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
                <div>
                    <p className="font-semibold">Modelo de Avaliação:</p>
                    <p className="text-muted-foreground">{metadata.eval_model || "N/A"}</p>
                </div>
                <div>
                    <p className="font-semibold">Modelo de Resposta:</p>
                    <p className="text-muted-foreground">{metadata.final_repose_model || "N/A"}</p>
                </div>
                <div>
                    <p className="font-semibold">Temperatura:</p>
                    <p className="text-muted-foreground">{metadata.temperature ?? "N/A"}</p>
                </div>
                <div>
                    <p className="font-semibold">Ferramentas:</p>
                    <p className="text-muted-foreground">{metadata.tools?.join(", ") || "N/A"}</p>
                </div>
                <PromptSection title="System Prompt Principal" content={metadata.system_prompt} collapseId="systemPromptCollapse" />
                <PromptSection title="System Prompt (Similaridade)" content={metadata.system_prompt_answer_similatiry} collapseId="systemPromptSimilarityCollapse" />
            </CardContent>
        </Card>
    );
}
