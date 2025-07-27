'use client';

import React from 'react';
import { marked } from 'marked';
import { Annotation } from '@/app/components/types';
import { Badge } from "@/components/ui/badge";

interface EvaluationsProps {
  annotations: Annotation[];
}

const getScoreBadgeClass = (score: number) => {
    if (score >= 0.8) {
      return 'bg-green-400 hover:bg-green-600 text-primary-foreground';
    } else if (score >= 0.5) {
      return 'bg-yellow-400 hover:bg-yellow-600 text-primary-foreground';
    } else {
      return 'bg-red-400 hover:bg-red-600 text-primary-foreground';
    }
  };

export default function Evaluations({ annotations }: EvaluationsProps) {
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

    return (
        <div className="space-y-2">
            {sortedAnnotations.map((ann, index) => (
                <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center gap-3">
                        <Badge className={getScoreBadgeClass(ann.score)}>
                            {ann.score.toFixed(1)}
                        </Badge>
                        <p className="font-semibold">{ann.name}</p>
                    </div>
                    {ann.explanation && (
                        <div className="prose prose-sm dark:prose-invert max-w-none mt-2 pt-2 border-t">
                            {typeof ann.explanation === 'string' ? (
                                <div dangerouslySetInnerHTML={{ __html: marked(ann.explanation) }} />
                            ) : (
                                <pre className="p-4 bg-muted text-muted-foreground rounded-md text-xs">
                                    {JSON.stringify(ann.explanation, null, 2)}
                                </pre>
                            )}
                        </div>
                    )}
                </div>
            ))}
        </div>
    );
}