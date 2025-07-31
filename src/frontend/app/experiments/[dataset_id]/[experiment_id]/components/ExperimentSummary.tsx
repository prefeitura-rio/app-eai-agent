'use client';

import React from 'react';
import { ExperimentDetails } from '../../../types';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Progress } from '@/components/ui/progress';

export default function ExperimentSummary({ experimentData }: { experimentData: ExperimentDetails }) {
    return (
        <div className="space-y-6">
            <Card>
                <CardHeader><CardTitle>Resumo da Execução</CardTitle></CardHeader>
                <CardContent className="grid grid-cols-3 gap-4 text-center">
                    <div>
                        <p className="text-sm text-muted-foreground">Duração Total</p>
                        <p className="text-2xl font-bold">{experimentData.execution_summary.total_duration_seconds.toFixed(2)}s</p>
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground">Duração Média/Task</p>
                        <p className="text-2xl font-bold">{experimentData.execution_summary.average_task_duration_seconds.toFixed(2)}s</p>
                    </div>
                    <div>
                        <p className="text-sm text-muted-foreground">Duração Média/Métrica</p>
                        <p className="text-2xl font-bold">{experimentData.execution_summary.average_metric_duration_seconds.toFixed(2)}s</p>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader><CardTitle>Métricas Agregadas</CardTitle></CardHeader>
                <CardContent>
                    {experimentData.aggregate_metrics.map(metric => (
                        <div key={metric.metric_name} className="mb-4 last:mb-0">
                            <h4 className="font-semibold text-base mb-2">{metric.metric_name}</h4>
                            <div className="text-xs text-muted-foreground grid grid-cols-2 gap-x-4 gap-y-1">
                                <span>Média: <strong className="text-foreground">{metric.score_statistics?.average?.toFixed(3) ?? 'N/A'}</strong></span>
                                <span>Mediana: <strong className="text-foreground">{metric.score_statistics?.median?.toFixed(3) ?? 'N/A'}</strong></span>
                                <span>Sucessos: <strong className="text-foreground text-green-600">{metric.successful_runs}</strong></span>
                                <span>Falhas: <strong className="text-foreground text-red-600">{metric.failed_runs}</strong></span>
                            </div>
                            <div className="mt-2">
                                <h5 className="text-sm font-medium mb-2">Distribuição de Scores</h5>
                                <div className="space-y-1">
                                    {metric.score_distribution.map((dist) => (
                                        <div key={dist.value} className="grid grid-cols-[3rem_1fr_5rem] items-center gap-2 text-xs">
                                            <div className="text-right font-bold">{dist.value.toFixed(1)}</div>
                                            <Progress value={dist.percentage} className="h-2" />
                                            <div className="text-left text-muted-foreground">({dist.count} runs) {dist.percentage.toFixed(0)}%</div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    ))}
                </CardContent>
            </Card>

            <Card>
                <CardHeader><CardTitle>Metadados do Experimento</CardTitle></CardHeader>
                <CardContent>
                    <Accordion type="multiple" className="w-full">
                        {Object.entries(experimentData.experiment_metadata).map(([key, value]) => (
                            <AccordionItem value={key} key={key}>
                                <AccordionTrigger className="capitalize">{key.replace(/_/g, ' ')}</AccordionTrigger>
                                <AccordionContent>
                                    <pre className="p-4 bg-muted rounded-md text-xs whitespace-pre-wrap break-all font-mono text-foreground">
                                        {JSON.stringify(value, null, 2)}
                                    </pre>
                                </AccordionContent>
                            </AccordionItem>
                        ))}
                    </Accordion>
                </CardContent>
            </Card>
            
            <div className="flex h-full items-center justify-center text-center text-muted-foreground pt-8">
                <p>Selecione um run na lista à esquerda para ver os detalhes completos.</p>
            </div>
        </div>
    );
}
