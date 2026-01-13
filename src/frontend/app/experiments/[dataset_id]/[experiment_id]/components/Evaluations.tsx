'use client';

import React, { useState, useEffect } from 'react';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import { Evaluation } from '../../../types';
import { Badge } from "@/components/ui/badge";
import { getScoreBadgeClass } from '@/app/utils/utils';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { AlertTriangle } from 'lucide-react';

const STORAGE_KEY = 'evaluations-visible-metrics';

/**
 * Checks if a string is a simple evaluator annotation format.
 */
const isEvaluatorAnnotation = (content: string): boolean => {
    const trimmed = content.trim();
    if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
        return false;
    }
    if (trimmed.startsWith('```')) {
        return false;
    }
    const hasEvaluatorFormat = /\*\*[^*]+:\*\*|^\d+\.\s/m.test(trimmed);
    const hasComplexMarkdown = /^#+\s|`{3}|\[.*\]\(.*\)/.test(trimmed);
    return hasEvaluatorFormat && !hasComplexMarkdown;
};

/**
 * Renders evaluator annotations with proper formatting.
 */
const EvaluatorAnnotationRenderer = ({ content }: { content: string }) => {
    const lines = content.split('\n');
    
    const processInlineFormatting = (text: string): React.ReactNode[] => {
        const result: React.ReactNode[] = [];
        let lastIndex = 0;
        const regex = /\*\*(.+?)\*\*/g;
        let match;
        
        while ((match = regex.exec(text)) !== null) {
            if (match.index > lastIndex) {
                result.push(text.slice(lastIndex, match.index));
            }
            result.push(<strong key={match.index}>{match[1]}</strong>);
            lastIndex = regex.lastIndex;
        }
        
        if (lastIndex < text.length) {
            result.push(text.slice(lastIndex));
        }
        
        return result.length > 0 ? result : [text];
    };
    
    const renderLine = (line: string, index: number) => {
        const trimmed = line.trim();
        
        if (!trimmed) {
            return <div key={index} className="h-2" />;
        }
        
        if (trimmed === '---') {
            return <hr key={index} className="my-2 border-border" />;
        }
        
        if (trimmed.startsWith('*') && trimmed.endsWith('*') && !trimmed.startsWith('**') && !trimmed.includes('**')) {
            const text = trimmed.slice(1, -1);
            return <p key={index} className="text-xs text-muted-foreground italic">{text}</p>;
        }
        
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
    
    if (typeof content === 'object' && content !== null) {
        return (
            <div className="p-4 bg-muted/50 border rounded-md">
                <pre className="text-xs font-mono whitespace-pre-wrap break-all text-foreground overflow-auto">
                    {JSON.stringify(content, null, 2)}
                </pre>
            </div>
        );
    }
    
    if (typeof content === 'string') {
        if (isEvaluatorAnnotation(content)) {
            return <EvaluatorAnnotationRenderer content={content} />;
        }
        
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
            marked.use({ breaks: true });
            const html = DOMPurify.sanitize(marked.parse(content) as string);
            
            return (
                <div
                    className="p-4 bg-muted/50 border rounded-md prose prose-sm dark:prose-invert max-w-none break-words"
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

// Hook to manage visible metrics with localStorage persistence
export function useVisibleMetrics(allMetrics: string[], storageKey: string = STORAGE_KEY) {
    const [selectedMetrics, setSelectedMetrics] = useState<string[]>(allMetrics);
    
    useEffect(() => {
        if (typeof window !== 'undefined') {
            const saved = localStorage.getItem(storageKey);
            if (saved) {
                try {
                    const parsed = JSON.parse(saved);
                    const validMetrics = parsed.filter((m: string) => allMetrics.includes(m));
                    if (validMetrics.length > 0) {
                        setSelectedMetrics(validMetrics);
                    }
                } catch {
                    // Ignore
                }
            }
        }
    }, [storageKey]); // eslint-disable-line react-hooks/exhaustive-deps
    
    useEffect(() => {
        if (typeof window !== 'undefined' && selectedMetrics.length > 0) {
            localStorage.setItem(storageKey, JSON.stringify(selectedMetrics));
        }
    }, [selectedMetrics, storageKey]);
    
    return { selectedMetrics, setSelectedMetrics };
}

// Main evaluations list component
interface EvaluationsProps {
    evaluations: Evaluation[];
    selectedMetrics: string[];
}

export default function Evaluations({ evaluations, selectedMetrics }: EvaluationsProps) {
    const visibleEvaluations = evaluations.filter(e => selectedMetrics.includes(e.metric_name));
    
    if (!evaluations || evaluations.length === 0) {
        return (
            <p className="text-muted-foreground p-4">Nenhuma avaliação para este modo.</p>
        );
    }
    
    if (visibleEvaluations.length === 0) {
        return (
            <div className="p-4 text-center text-muted-foreground border rounded-md">
                Nenhuma métrica selecionada. Use o seletor acima para escolher métricas.
            </div>
        );
    }

    return (
        <Accordion type="multiple" defaultValue={visibleEvaluations.map(e => e.metric_name)}>
            {visibleEvaluations.map((ev) => (
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
