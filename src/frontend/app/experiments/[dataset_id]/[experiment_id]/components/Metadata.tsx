'use client';

import React from 'react';
import { ExperimentDetails } from '../../../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Settings } from 'lucide-react';

interface MetadataProps {
  metadata: ExperimentDetails['experiment_metadata'];
}

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
            <CardContent>
                <Accordion type="multiple" className="w-full">
                    {Object.entries(metadata).map(([key, value]) => (
                        <AccordionItem value={key} key={key}>
                            <AccordionTrigger className="capitalize">{key.replace(/_/g, ' ')}</AccordionTrigger>
                            <AccordionContent>
                                <pre className="p-4 bg-muted rounded-md text-xs whitespace-pre-wrap break-all font-mono text-foreground">
                                    {JSON.stringify(value, null, 2)}
                                </pre>
                            </AccordionContent>
                        </AccordionItem>
                    ))}
                </Accordion>
            </CardContent>
        </Card>
    );
}
