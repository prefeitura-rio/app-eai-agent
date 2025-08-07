'use client';

import React, { ReactNode } from 'react';
import { ExperimentDetails } from '../../../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Settings } from 'lucide-react';

export default function ExperimentSummary({ experimentData }: { experimentData: ExperimentDetails }) {
    if (!experimentData) {
        return <div className="text-center text-muted-foreground">Carregando dados do experimento...</div>;
    }
    
    const metadata = experimentData.experiment_metadata || {};
    const judgesPrompts = metadata.judges_prompts; // Variável para facilitar a verificação de tipo

    const renderValue = (value: unknown): ReactNode => {
        if (value === null || value === undefined) {
            return <span className="text-muted-foreground italic">N/A</span>;
        }
        if (typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') {
            return <p className="text-xs leading-tight">{String(value)}</p>;
        }
        try {
            const stringified = JSON.stringify(value, null, 2);
            return (
                <pre className="text-xs whitespace-pre-wrap break-all font-mono leading-tight">
                    {stringified}
                </pre>
            );
        } catch {
            return <span className="text-muted-foreground italic">Não foi possível exibir o valor</span>;
        }
    };
    
    return (
        <div className="space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-lg">
                        <Settings className="h-5 w-5 text-primary" />
                        <span>Metadados do Experimento</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="space-y-4">
                        {/* Campos diretos em grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {Object.entries(metadata)
                                .filter(([key]) => !['judges_prompts', 'system_prompt'].includes(key))
                                .map(([key, value]): React.ReactElement => (
                                    <div key={key} className="space-y-1">
                                        <h4 className="font-semibold text-xs capitalize text-muted-foreground">
                                            {key.replace(/_/g, ' ')}
                                        </h4>
                                        <div className="p-2 rounded-md min-h-[60px] flex items-center">
                                            {renderValue(value)}
                                        </div>
                                    </div>
                                ))}
                        </div>
                        
                        {/* System Prompt - CORRIGIDO */}
                        {/* Envolvemos a condição com Boolean() para garantir que seja um booleano. */}
                        {Boolean(metadata.system_prompt) && (
                            <Accordion type="multiple" className="w-full">
                                <AccordionItem value="system_prompt">
                                    <AccordionTrigger className="capitalize">System Prompt</AccordionTrigger>
                                    <AccordionContent>
                                        <div className="p-4 rounded-md text-xs whitespace-pre-wrap break-all font-mono text-foreground bg-muted/50 border">
                                            {String(metadata.system_prompt)}
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>
                            </Accordion>
                        )}
                        
                        {/* Judges Prompts - CORRIGIDO e MAIS SEGURO */}
                        {/* Verificamos se 'judgesPrompts' é um objeto e tem chaves antes de renderizar. */}
                        {typeof judgesPrompts === 'object' && judgesPrompts !== null && Object.keys(judgesPrompts).length > 0 && (
                            <Accordion type="multiple" className="w-full">
                                <AccordionItem value="judges_prompts">
                                    <AccordionTrigger className="capitalize">Judges Prompts</AccordionTrigger>
                                    <AccordionContent>
                                        <Tabs defaultValue={Object.keys(judgesPrompts)[0]} className="w-full">
                                            <TabsList>
                                                {Object.keys(judgesPrompts).map(key => (
                                                    <TabsTrigger key={key} value={key} className="text-xs">
                                                        {key.replace(/_/g, ' ')}
                                                    </TabsTrigger>
                                                ))}
                                            </TabsList>
                                            {Object.entries(judgesPrompts).map(([key, value]) => (
                                                <TabsContent key={key} value={key}>
                                                    <div className="p-4 rounded-md text-xs whitespace-pre-wrap break-all font-mono text-foreground bg-muted/50 border">
                                                        {String(value)}
                                                    </div>
                                                </TabsContent>
                                            ))}
                                        </Tabs>
                                    </AccordionContent>
                                </AccordionItem>
                            </Accordion>
                        )}
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}