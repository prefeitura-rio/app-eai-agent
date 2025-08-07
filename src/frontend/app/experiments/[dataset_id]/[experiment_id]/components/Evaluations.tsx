'use client';

import React from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { Evaluation } from '../../../types';
import { Badge } from "@/components/ui/badge";
import { getScoreBadgeClass } from '@/app/utils/utils';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { AlertTriangle, FileText } from 'lucide-react';

interface EvaluationsProps {
  evaluations: Evaluation[];
}

const MarkdownRenderer = ({ content }: { content: string | Record<string, unknown> | null }) => {
    if (!content) return null;
    
    // Convert object to formatted string if needed
    let contentString: string;
    let isJson = false;
    
    if (typeof content === 'string') {
        contentString = content;
    } else {
        contentString = JSON.stringify(content, null, 2);
        isJson = true;
    }
    
    // If it's JSON, render as formatted JSON
    if (isJson) {
        return (
            <div className="p-4 bg-muted/50 border rounded-md">
                <pre className="text-xs whitespace-pre-wrap break-all font-mono text-foreground">
                    {contentString}
                </pre>
            </div>
        );
    }
    
    // If it's markdown, render as HTML
    marked.use({ breaks: true });
    const html = DOMPurify.sanitize(marked.parse(contentString) as string);
    return (
        <div
            className="prose prose-sm dark:prose-invert max-w-none p-4 bg-muted/50 border rounded-md"
            dangerouslySetInnerHTML={{ __html: html }}
        />
    );
};

export default function Evaluations({ evaluations }: EvaluationsProps) {
    if (!evaluations || evaluations.length === 0) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle className="flex items-center gap-3 text-lg">
                        <FileText className="h-5 w-5 text-primary" />
                        <span>Avaliações</span>
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground p-4">Nenhuma avaliação para este modo.</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-3 text-lg">
                    <FileText className="h-5 w-5 text-primary" />
                    <span>Avaliações</span>
                </CardTitle>
            </CardHeader>
            <CardContent>
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
            </CardContent>
        </Card>
    );
}
