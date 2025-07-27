'use client';

import React, { useMemo } from 'react';
import { Run } from '@/app/components/types';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { BarChart2 } from 'lucide-react';

interface SummaryMetricsProps {
  runs: Run[];
}

export default function SummaryMetrics({ runs }: SummaryMetricsProps) {
    const summary = useMemo(() => {
        const metrics: { [key: string]: { scores: number[], counts: { [key: string]: number } } } = {};
        if (!runs) return { metrics: {}, totalRuns: 0 };

        runs.forEach((run) => {
            run.annotations?.forEach((ann) => {
                if (typeof ann.score === 'number' && !isNaN(ann.score)) {
                    if (!metrics[ann.name]) {
                        metrics[ann.name] = { scores: [], counts: {} };
                    }
                    metrics[ann.name].scores.push(ann.score);
                    const scoreStr = ann.score.toFixed(1);
                    metrics[ann.name].counts[scoreStr] = (metrics[ann.name].counts[scoreStr] || 0) + 1;
                }
            });
        });
        return { metrics, totalRuns: runs.length };
    }, [runs]);

    if (summary.totalRuns === 0) return null;

    const preferredOrder = [
        "Answer Completeness", "Answer Similarity", "Activate Search Tools",
        "Golden Link in Answer", "Golden Link in Tool Calling",
    ];

    const sortedMetricNames = Object.keys(summary.metrics).sort((a, b) => {
        const indexA = preferredOrder.indexOf(a);
        const indexB = preferredOrder.indexOf(b);
        if (indexA !== -1 && indexB !== -1) return indexA - indexB;
        if (indexA !== -1) return -1;
        if (indexB !== -1) return 1;
        return a.localeCompare(b);
    });

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-3 text-lg">
                    <BarChart2 className="h-5 w-5 text-primary" />
                    <span>Métricas Gerais</span>
                </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {sortedMetricNames.map(name => {
                    const metric = summary.metrics[name];
                    if (!metric || metric.scores.length === 0) return null;
                    const average = metric.scores.reduce((a, b) => a + b, 0) / metric.scores.length;
                    return (
                        <Card key={name} className="flex flex-col">
                            <CardHeader className="pb-2">
                                <CardDescription>{name}</CardDescription>
                                <CardTitle className="text-2xl">{average.toFixed(2)}</CardTitle>
                            </CardHeader>
                            <CardContent>
                                {/* Distribution can be added here */}
                            </CardContent>
                        </Card>
                    );
                })}
            </CardContent>
        </Card>
    );
}