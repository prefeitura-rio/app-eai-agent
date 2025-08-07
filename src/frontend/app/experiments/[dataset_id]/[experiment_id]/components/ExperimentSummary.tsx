'use client';

import React from 'react';
import { ExperimentDetails } from '../../../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Settings } from 'lucide-react';

export default function ExperimentSummary({ experimentData }: { experimentData: ExperimentDetails }) {
    // Verificações de segurança
    if (!experimentData) {
        return <div className="text-center text-muted-foreground">Carregando dados do experimento...</div>;
    }
    
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
                        {/* Campos diretos em grid de 4 colunas */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                            {Object.entries(experimentData.experiment_metadata || {})
                                .filter(([key]) => !['judges_prompts', 'system_prompt'].includes(key))
                                .map(([key, value]) => {
                                    const displayValue = typeof value === 'string' ? value : JSON.stringify(value, null, 2);
                                    return (
                                        <div key={key} className="space-y-1">
                                            <h4 className="font-semibold text-xs capitalize text-muted-foreground">{key.replace(/_/g, ' ')}</h4>
                                            <div className="p-2 rounded-md min-h-[60px] flex items-center">
                                                {typeof value === 'string' ? (
                                                    <p className="text-xs leading-tight">{displayValue}</p>
                                                ) : (
                                                    <pre className="text-xs whitespace-pre-wrap break-all font-mono leading-tight">
                                                        {displayValue}
                                                    </pre>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
                        </div>
                        
                        {/* System Prompt */}
                        {experimentData.experiment_metadata?.system_prompt && (
                            <Accordion type="multiple" className="w-full">
                                <AccordionItem value="system_prompt">
                                    <AccordionTrigger className="capitalize">System Prompt</AccordionTrigger>
                                    <AccordionContent>
                                        <div className="p-4 rounded-md text-xs whitespace-pre-wrap break-all font-mono text-foreground bg-muted/50 border">
                                            {String(experimentData.experiment_metadata.system_prompt)}
                                        </div>
                                    </AccordionContent>
                                </AccordionItem>
                            </Accordion>
                        )}
                        
                        {/* Judges Prompts */}
                        {experimentData.experiment_metadata?.judges_prompts && Object.keys(experimentData.experiment_metadata.judges_prompts).length > 0 && (
                            <Accordion type="multiple" className="w-full">
                                <AccordionItem value="judges_prompts">
                                    <AccordionTrigger className="capitalize">Judges Prompts</AccordionTrigger>
                                    <AccordionContent>
                                        <Tabs defaultValue={Object.keys(experimentData.experiment_metadata.judges_prompts)[0]} className="w-full">
                                            <TabsList>
                                                {Object.keys(experimentData.experiment_metadata.judges_prompts).map(key => (
                                                    <TabsTrigger key={key} value={key} className="text-xs">{key.replace(/_/g, ' ')}</TabsTrigger>
                                                ))}
                                            </TabsList>
                                            {Object.entries(experimentData.experiment_metadata.judges_prompts).map(([key, value]) => (
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
