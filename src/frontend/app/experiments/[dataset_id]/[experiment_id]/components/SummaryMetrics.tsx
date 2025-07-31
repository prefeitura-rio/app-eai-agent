'use client';

import React from 'react';
import { ExperimentDetails } from '../../../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { BarChart2 } from 'lucide-react';

interface SummaryMetricsProps {
  aggregateMetrics: ExperimentDetails['aggregate_metrics'];
}

export default function SummaryMetrics({ aggregateMetrics }: SummaryMetricsProps) {
    if (!aggregateMetrics || aggregateMetrics.length === 0) return null;

    return (
        <Card>
            <CardHeader>
                <CardTitle className="flex items-center gap-3 text-lg">
                    <BarChart2 className="h-5 w-5 text-primary" />
                    <span>Métricas Gerais</span>
                </CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {aggregateMetrics.map(metric => (
                    <Card key={metric.metric_name} className="flex flex-col">
                        <CardHeader className="pb-2">
                            <CardTitle>{metric.metric_name}</CardTitle>
                            <p className="text-2xl font-bold text-primary">{metric.score_statistics?.average?.toFixed(2) ?? 'N/A'} avg.</p>
                        </CardHeader>
                        <CardContent>
                            <hr className="mb-2" />
                            <div className="space-y-2">
                                {metric.score_distribution.map((dist: any) => (
                                    <div key={dist.value} className="grid grid-cols-[2rem_1fr_4rem] items-center gap-2 text-xs">
                                        <div className="text-right">{dist.value.toFixed(1)}</div>
                                        <Progress value={dist.percentage} className="h-2" />
                                        <div className="text-left text-muted-foreground">({dist.count}) {dist.percentage.toFixed(0)}%</div>
                                    </div>
                                ))}
                            </div>
                        </CardContent>
                    </Card>
                ))}
            </CardContent>
        </Card>
    );
}
