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

/**
 * Checks if a string is a simple human-readable text (not JSON, not markdown).
 * Simple text is text that doesn't contain JSON or complex markdown formatting.
 */
const isSimpleText = (content: string): boolean => {
    const trimmed = content.trim();
    // Not JSON (doesn't start with { or [)
    if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
        return false;
    }
    // Not code blocks
    if (trimmed.startsWith('```')) {
        return false;
    }
    // Contains mostly readable text (no heavy markdown)
    // Allow basic punctuation but not markdown syntax
    const hasComplexMarkdown = /^#+\s|`{3}|\*\*|__|\[.*\]\(.*\)/.test(trimmed);
    return !hasComplexMarkdown;
};

/**
 * Renders a simple text annotation as a clean, styled text block.
 * Preserves newlines by splitting content into paragraphs.
 */
const SimpleTextRenderer = ({ content }: { content: string }) => {
    const lines = content.split('\n');
    return (
        <div className="p-4 bg-muted/50 border rounded-md">
            <div className="text-sm text-foreground leading-relaxed space-y-1">
                {lines.map((line, i) => (
                    <p key={i}>{line || '\u00A0'}</p>
                ))}
            </div>
        </div>
    );
};

const MarkdownRenderer = ({ content }: { content: string | Record<string, unknown> | null }) => {
    if (!content) return null;
    
    // If it's an object, render as JSON
    if (typeof content === 'object' && content !== null) {
        return (
            <div className="p-4 bg-muted/50 border rounded-md">
                <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
                    {JSON.stringify(content, null, 2)}
                </pre>
            </div>
        );
    }
    
    // If it's a string
    if (typeof content === 'string') {
        // First, check if it's simple human-readable text (new evaluators format)
        if (isSimpleText(content)) {
            return <SimpleTextRenderer content={content} />;
        }
        
        // Try to parse as JSON
        try {
            const parsed = JSON.parse(content);
            return (
                <div className="p-4 bg-muted/50 border rounded-md">
                    <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
                        {JSON.stringify(parsed, null, 2)}
                    </pre>
                </div>
            );
        } catch {
            // If not JSON, render as markdown
            marked.use({ breaks: true });
            const html = DOMPurify.sanitize(marked.parse(content) as string);
            // Check if the content is just simple text wrapped in code blocks
            const isSimpleTextInCodeBlock = content.trim().startsWith('```') && 
                                          content.trim().endsWith('```') && 
                                          !content.includes('**') && 
                                          !content.includes('*') && 
                                          !content.includes('[') && 
                                          !content.includes(']') &&
                                          !content.includes('#');
            
            
            if (isSimpleTextInCodeBlock) {
                // Extract the content without the code block markers
                const cleanContent = content.trim().replace(/^```\s*/, '').replace(/\s*```$/, '');
                return (
                    <div
                        className="p-4 bg-muted/50 border rounded-md prose prose-sm dark:prose-invert max-w-none break-words overflow-wrap-anywhere"
                        style={{
                            wordBreak: 'break-word',
                            overflowWrap: 'break-word',
                            whiteSpace: 'pre-wrap',
                            maxWidth: '100%',
                            overflow: 'visible'
                        }}
                        dangerouslySetInnerHTML={{ __html: `<p style="word-break: break-word; overflow-wrap: break-word; white-space: pre-wrap; max-width: 100%;">${cleanContent}</p>` }}
                    />
                );
            }
            
            return (
                <div
                    className="p-4 bg-muted/50 border rounded-md prose prose-sm dark:prose-invert max-w-none break-words overflow-wrap-anywhere"
                    style={{
                        wordBreak: 'break-word',
                        overflowWrap: 'break-word',
                        whiteSpace: 'pre-wrap',
                        maxWidth: '100%',
                        overflow: 'visible'
                    }}
                    dangerouslySetInnerHTML={{ __html: html }}

                />
            );
        }
    }
    
    return null;
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
                    <p className="text-base-custom text-muted-foreground p-4">Nenhuma avaliação para este modo.</p>
                </CardContent>
            </Card>
        );
    }

    return (
        <Accordion type="multiple" defaultValue={evaluations.map(e => e.metric_name)}>
            {evaluations.map((ev) => {
                return (
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
                            <div>
                                <MarkdownRenderer content={ev.annotations} />
                            </div>
                        </AccordionContent>
                    </AccordionItem>
                );
            })}
        </Accordion>
    );
}
