'use client';

import React, { useState, useEffect } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { Annotation } from '@/app/components/types';
import { Badge } from "@/components/ui/badge";
import { getScoreBadgeClass } from '@/app/utils/utils';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';

interface EvaluationsProps {
  annotations: Annotation[];
}

const isJsonString = (str: string) => {
    try {
        JSON.parse(str);
    } catch {
        return false;
    }
    return true;
};

export default function Evaluations({ annotations }: EvaluationsProps) {
    const [renderedExplanations, setRenderedExplanations] = useState<(string | Record<string, unknown>)[]>([]);

    useEffect(() => {
        const processExplanations = () => {
            const processed = annotations.map((ann) => {
                if (typeof ann.explanation === 'string' && !isJsonString(ann.explanation)) {
                    return DOMPurify.sanitize(marked.parse(ann.explanation) as string);
                }
                return ann.explanation;
            });
            setRenderedExplanations(processed);
        };
        processExplanations();
    }, [annotations]);

    if (!annotations || annotations.length === 0) {
        return <p className="text-sm text-muted-foreground">Nenhuma avaliação disponível.</p>;
    }

    const preferredOrder = [
        "Answer Completeness", "Answer Similarity", "Activate Search Tools",
        "Golden Link in Answer", "Golden Link in Tool Calling",
    ];

    const sortedAnnotations = [...annotations].sort((a, b) => {
        const indexA = preferredOrder.indexOf(a.name);
        const indexB = preferredOrder.indexOf(b.name);
        if (indexA !== -1 && indexB !== -1) return indexA - indexB;
        if (indexA !== -1) return -1;
        if (indexB !== -1) return 1;
        return a.name.localeCompare(b.name);
    });

    const defaultOpen = sortedAnnotations
        .map((ann, index) => `item-${index}`)
        .filter((_, index) => !["Golden Link in Answer", "Golden Link in Tool Calling"].includes(sortedAnnotations[index].name));

    return (
        <Accordion type="multiple" defaultValue={defaultOpen}>
            {sortedAnnotations.map((ann, index) => (
                <AccordionItem value={`item-${index}`} key={index}>
                    <AccordionTrigger className="hover:no-underline">
                        <div className="flex items-center gap-3">
                            <Badge className={getScoreBadgeClass(ann.score)}>
                                {ann.score.toFixed(1)}
                            </Badge>
                            <span className="font-semibold text-left">{ann.name}</span>
                        </div>
                    </AccordionTrigger>
                    <AccordionContent className="pl-12">
                        {ann.explanation && (
                            <div className="prose prose-sm dark:prose-invert max-w-none">
                                {typeof ann.explanation === 'string' && isJsonString(ann.explanation) ? (
                                    <pre className="p-4 bg-muted rounded-md text-xs whitespace-pre-wrap break-all text-foreground">
                                        {JSON.stringify(JSON.parse(ann.explanation), null, 2)}
                                    </pre>
                                ) : typeof ann.explanation === 'string' ? (
                                    <div dangerouslySetInnerHTML={{ __html: renderedExplanations[index] as string }} />
                                ) : (
                                    <pre className="p-4 bg-muted rounded-md text-xs whitespace-pre-wrap break-all text-foreground">
                                        {JSON.stringify(ann.explanation, null, 2)}
                                    </pre>
                                )}
                            </div>
                        )}
                    </AccordionContent>
                </AccordionItem>
            ))}
        </Accordion>
    );
}