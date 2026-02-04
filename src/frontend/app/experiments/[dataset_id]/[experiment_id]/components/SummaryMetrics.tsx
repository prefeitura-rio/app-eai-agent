'use client';

import React, { useMemo } from 'react';
import { ExperimentDetails } from '../../../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { BarChart2, ChevronDown, ChevronUp } from 'lucide-react';
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import MetricsSelector from './MetricsSelector';

interface SummaryMetricsProps {
  aggregateMetrics: ExperimentDetails['aggregate_metrics'];
  visibleMetrics: string[];
  onVisibleMetricsChange: (metrics: string[]) => void;
}

function getScoreColor(score: number | undefined | null): string {
    if (score === undefined || score === null) return 'text-muted-foreground';
    if (score >= 0.8) return 'text-green-600 dark:text-green-400';
    if (score >= 0.5) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
}

function getScoreBgColor(score: number | undefined | null): string {
    if (score === undefined || score === null) return 'bg-muted';
    if (score >= 0.8) return 'bg-green-100 dark:bg-green-900/30';
    if (score >= 0.5) return 'bg-yellow-100 dark:bg-yellow-900/30';
    return 'bg-red-100 dark:bg-red-900/30';
}

export default function SummaryMetrics({ 
    aggregateMetrics, 
    visibleMetrics,
    onVisibleMetricsChange,
}: SummaryMetricsProps) {
    const [isExpanded, setIsExpanded] = React.useState(true);
    
    const allMetricNames = useMemo(() => 
        aggregateMetrics?.map(m => m.metric_name) || [],
        [aggregateMetrics]
    );
    
    const filteredMetrics = useMemo(() => 
        aggregateMetrics?.filter(m => visibleMetrics.includes(m.metric_name)) || [],
        [aggregateMetrics, visibleMetrics]
    );

    if (!aggregateMetrics || aggregateMetrics.length === 0) return null;

    return (
        <Card>
            <Collapsible open={isExpanded} onOpenChange={setIsExpanded}>
                <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                        <CollapsibleTrigger asChild>
                            <Button variant="ghost" className="p-0 h-auto hover:bg-transparent">
                                <CardTitle className="flex items-center gap-3 text-lg cursor-pointer">
                                    <BarChart2 className="h-5 w-5 text-primary" />
                                    <span>Métricas Gerais</span>
                                    {isExpanded ? (
                                        <ChevronUp className="h-4 w-4 text-muted-foreground" />
                                    ) : (
                                        <ChevronDown className="h-4 w-4 text-muted-foreground" />
                                    )}
                                </CardTitle>
                            </Button>
                        </CollapsibleTrigger>
                        <div className="flex items-center gap-2">
                            <MetricsSelector
                                availableMetrics={allMetricNames}
                                selectedMetrics={visibleMetrics}
                                onSelectionChange={onVisibleMetricsChange}
                            />
                        </div>
                    </div>
                    
                    {/* Compact summary when collapsed */}
                    {!isExpanded && filteredMetrics.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                            {filteredMetrics.map(metric => (
                                <Badge 
                                    key={metric.metric_name} 
                                    variant="outline"
                                    className={`${getScoreBgColor(metric.score_statistics?.average)} border-0`}
                                >
                                    <span className="font-normal mr-1">{metric.metric_name}:</span>
                                    <span className={`font-semibold ${getScoreColor(metric.score_statistics?.average)}`}>
                                        {metric.score_statistics?.average?.toFixed(2) ?? 'N/A'}
                                    </span>
                                </Badge>
                            ))}
                        </div>
                    )}
                </CardHeader>
                
                <CollapsibleContent>
                    <CardContent className="pt-2">
                        {filteredMetrics.length === 0 ? (
                            <p className="text-muted-foreground text-sm text-center py-4">
                                Nenhuma métrica selecionada. Use o botão &quot;Colunas&quot; para selecionar métricas.
                            </p>
                        ) : (
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                                {filteredMetrics.map(metric => (
                                    <Card key={metric.metric_name} className={`flex flex-col ${getScoreBgColor(metric.score_statistics?.average)}`}>
                                        <CardHeader className="pb-2 pt-3 px-3">
                                            <CardTitle className="text-sm font-medium truncate" title={metric.metric_name}>
                                                {metric.metric_name}
                                            </CardTitle>
                                            <p className={`text-xl font-bold ${getScoreColor(metric.score_statistics?.average)}`}>
                                                {metric.score_statistics?.average?.toFixed(2) ?? 'N/A'}
                                                <span className="text-xs font-normal text-muted-foreground ml-1">avg</span>
                                            </p>
                                        </CardHeader>
                                        <CardContent className="px-3 pb-3 pt-0">
                                            <div className="space-y-1">
                                                {metric.score_distribution.map((dist) => (
                                                    <div key={dist.value} className="grid grid-cols-[1.5rem_1fr_3rem] items-center gap-1 text-xs">
                                                        <div className="text-right text-muted-foreground">{dist.value.toFixed(1)}</div>
                                                        <Progress value={dist.percentage} className="h-1.5" />
                                                        <div className="text-left text-muted-foreground">{dist.percentage.toFixed(0)}%</div>
                                                    </div>
                                                ))}
                                            </div>
                                        </CardContent>
                                    </Card>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </CollapsibleContent>
            </Collapsible>
        </Card>
    );
}
