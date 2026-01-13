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
 * Checks if a string is a simple evaluator annotation format.
 * This format uses ** for bold headers and numbered lists, but not complex markdown.
 */
const isEvaluatorAnnotation = (content: string): boolean => {
    const trimmed = content.trim();
    // Not JSON (doesn't start with { or [)
    if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
        return false;
    }
    // Not code blocks
    if (trimmed.startsWith('```')) {
        return false;
    }
    // Check for evaluator annotation patterns: **Header:** or numbered lists
    const hasEvaluatorFormat = /\*\*[^*]+:\*\*|^\d+\.\s/m.test(trimmed);
    // Has complex markdown like headers, links, or code
    const hasComplexMarkdown = /^#+\s|`{3}|\[.*\]\(.*\)/.test(trimmed);
    return hasEvaluatorFormat && !hasComplexMarkdown;
};

/**
 * Renders evaluator annotations with proper formatting.
 * Handles **bold** text, *italic* descriptions, and numbered lists.
 */
const EvaluatorAnnotationRenderer = ({ content }: { content: string }) => {
    const lines = content.split('\n');
    
    // Process inline formatting: **bold**
    const processInlineFormatting = (text: string): React.ReactNode[] => {
        const result: React.ReactNode[] = [];
        let lastIndex = 0;
        const regex = /\*\*(.+?)\*\*/g;
        let match;
        
        while ((match = regex.exec(text)) !== null) {
            // Add text before the match
            if (match.index > lastIndex) {
                result.push(text.slice(lastIndex, match.index));
            }
            // Add the bold text
            result.push(<strong key={match.index}>{match[1]}</strong>);
            lastIndex = regex.lastIndex;
        }
        
        // Add remaining text
        if (lastIndex < text.length) {
            result.push(text.slice(lastIndex));
        }
        
        return result.length > 0 ? result : [text];
    };
    
    const renderLine = (line: string, index: number) => {
        const trimmed = line.trim();
        
        // Empty line = small spacer
        if (!trimmed) {
            return <div key={index} className="h-2" />;
        }
        
        // Horizontal rule
        if (trimmed === '---') {
            return <hr key={index} className="my-2 border-border" />;
        }
        
        // Italic description line (starts and ends with single *, no ** inside)
        if (trimmed.startsWith('*') && trimmed.endsWith('*') && !trimmed.startsWith('**') && !trimmed.includes('**')) {
            const text = trimmed.slice(1, -1);
            return <p key={index} className="text-xs text-muted-foreground italic">{text}</p>;
        }
        
        // Regular line - process bold formatting
        return <p key={index}>{processInlineFormatting(line)}</p>;
    };
    
    return (
        <div className="p-4 bg-muted/50 border rounded-md">
            <div className="text-sm text-foreground leading-relaxed">
                {lines.map((line, i) => renderLine(line, i))}
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
        // First, check if it's evaluator annotation format
        if (isEvaluatorAnnotation(content)) {
            return <EvaluatorAnnotationRenderer content={content} />;
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
