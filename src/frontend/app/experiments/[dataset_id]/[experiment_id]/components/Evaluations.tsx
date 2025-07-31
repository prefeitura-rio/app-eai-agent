'use client';

import React from 'react';
import { ExperimentRun } from '../../../types';
import { Badge } from "@/components/ui/badge";
import { getScoreBadgeClass } from '@/app/utils/utils';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';

interface EvaluationsProps {
  evaluations: ExperimentRun['evaluations'];
}

export default function Evaluations({ evaluations }: EvaluationsProps) {
    if (!evaluations || evaluations.length === 0) {
        return <p className="text-sm text-muted-foreground p-4">Nenhuma avaliação para este modo.</p>;
    }

    return (
        <Accordion type="multiple" defaultValue={evaluations.map(e => e.metric_name)}>
            {evaluations.map((ev) => (
                <AccordionItem value={ev.metric_name} key={ev.metric_name}>
                    <AccordionTrigger className="hover:no-underline">
                        <div className="flex items-center gap-3">
                            <Badge className={getScoreBadgeClass(ev.score || 0)}>
                                {ev.score?.toFixed(1) ?? 'N/A'}
                            </Badge>
                            <span className="font-semibold text-left">{ev.metric_name}</span>
                        </div>
                    </AccordionTrigger>
                    <AccordionContent className="pl-12">
                        <pre className="p-4 bg-muted rounded-md text-xs whitespace-pre-wrap break-all text-foreground">
                            {ev.judge_annotations}
                        </pre>
                    </AccordionContent>
                </AccordionItem>
            ))}
        </Accordion>
    );
}
