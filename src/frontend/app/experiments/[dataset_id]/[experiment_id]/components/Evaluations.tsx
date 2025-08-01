'use client';

import React from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { Evaluation } from '../../../types';
import { Badge } from "@/components/ui/badge";
import { getScoreBadgeClass } from '@/app/utils/utils';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { AlertTriangle } from 'lucide-react';

interface EvaluationsProps {
  evaluations: Evaluation[];
}

const MarkdownRenderer = ({ content }: { content: string | null }) => {
    if (!content) return null;
    marked.use({ breaks: true });
    const html = DOMPurify.sanitize(marked.parse(content) as string);
    return (
        <div
            className="prose prose-sm dark:prose-invert max-w-none p-4 bg-muted rounded-md"
            dangerouslySetInnerHTML={{ __html: html }}
        />
    );
};

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
                            <Badge className={getScoreBadgeClass(ev.score ?? 0)}>
                                {ev.score?.toFixed(1) ?? 'N/A'}
                            </Badge>
                            <span className="font-semibold text-left">{ev.metric_name}</span>
                            {ev.has_error && <AlertTriangle className="h-4 w-4 text-destructive" />}
                        </div>
                    </AccordionTrigger>
                    <AccordionContent>
                        <MarkdownRenderer content={ev.annotations} />
                    </AccordionContent>
                </AccordionItem>
            ))}
        </Accordion>
    );
}
