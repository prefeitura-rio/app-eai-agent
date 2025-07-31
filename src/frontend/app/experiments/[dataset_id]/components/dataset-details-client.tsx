'use client';

import React, { useState, useMemo, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import ProgressBar from './ProgressBar';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import { Search, ArrowUp, ArrowDown, RefreshCw } from 'lucide-react';
import { useHeader } from '@/app/contexts/HeaderContext';
import { DatasetExperimentInfo, DatasetExample } from '../../types';

interface ClientProps {
  experiments: DatasetExperimentInfo[];
  examples: DatasetExample[];
  datasetId: string;
}

type SortKey = keyof DatasetExperimentInfo;

export default function DatasetDetailsClient({ 
  experiments: initialExperiments, 
  examples: initialExamples, 
  datasetId
}: ClientProps) {
  const router = useRouter();
  const { setTitle, setSubtitle } = useHeader();
  
  const [experiments] = useState<DatasetExperimentInfo[]>(initialExperiments);
  const [examples] = useState<DatasetExample[]>(initialExamples);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState<{ key: SortKey | null; direction: 'ascending' | 'descending' }>({ key: 'experiment_timestamp', direction: 'descending' });

  const datasetName = initialExperiments[0]?.dataset_name || `Dataset ${datasetId}`;

  useEffect(() => {
    setTitle('Experimentos do Dataset');
    setSubtitle(datasetName);
  }, [setTitle, setSubtitle, datasetName]);

  const allMetrics = useMemo(() => {
    const metrics = new Set<string>();
    experiments.forEach(exp => {
      exp.aggregate_metrics.forEach(metric => metrics.add(metric.metric_name));
    });
    return Array.from(metrics).sort();
  }, [experiments]);

  const filteredAndSortedExperiments = useMemo(() => {
    let sortableItems = [...experiments];
    if (searchTerm) {
      sortableItems = sortableItems.filter(item =>
        item.experiment_name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    if (sortConfig.key) {
      sortableItems.sort((a, b) => {
        const aValue = a[sortConfig.key!];
        const bValue = b[sortConfig.key!];
        if (aValue < bValue) return sortConfig.direction === 'ascending' ? -1 : 1;
        if (aValue > bValue) return sortConfig.direction === 'ascending' ? 1 : -1;
        return 0;
      });
    }
    return sortableItems;
  }, [experiments, searchTerm, sortConfig]);

  const filteredExamples = useMemo(() => {
    if (!searchTerm) return examples;
    return examples.filter(ex => {
      const content = JSON.stringify(ex);
      return content.toLowerCase().includes(searchTerm.toLowerCase());
    });
  }, [examples, searchTerm]);

  const requestSort = (key: SortKey) => {
    let direction: 'ascending' | 'descending' = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };
  
  const handleRowClick = (experimentId: string) => {
    router.push(`/experiments/${datasetId}/${experimentId}`);
  };

  const formatObjectForDisplay = (obj: Record<string, unknown>) => {
    if (!obj) return '';
    return JSON.stringify(obj, null, 2);
  };

  const SortableHeader = ({ sortKey, children, className }: { sortKey: SortKey, children: React.ReactNode, className?: string }) => (
    <TableHead className={className}>
        <Button variant="ghost" onClick={() => requestSort(sortKey)} className="w-full justify-start px-2 text-xs uppercase">
            {children}
            {sortConfig.key === sortKey && (
                sortConfig.direction === 'ascending' ? <ArrowUp className="ml-2 h-4 w-4" /> : <ArrowDown className="ml-2 h-4 w-4" />
            )}
        </Button>
    </TableHead>
  );

  return (
    <Tabs defaultValue="experiments" className="w-full space-y-4">
        <div className="flex items-center justify-between">
            <TabsList>
                <TabsTrigger value="experiments">Experimentos ({filteredAndSortedExperiments.length})</TabsTrigger>
                <TabsTrigger value="examples">Exemplos ({filteredExamples.length})</TabsTrigger>
            </TabsList>
            <div className="flex items-center justify-between gap-4">
                <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      type="text"
                      placeholder="Filtrar..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-9"
                    />
                </div>
                <Tooltip>
                  <TooltipTrigger asChild>
                    <Button variant="outline" size="icon" onClick={() => window.location.reload()}>
                      <RefreshCw className="h-4 w-4 text-primary" />
                    </Button>
                  </TooltipTrigger>
                  <TooltipContent><p>Atualizar</p></TooltipContent>
                </Tooltip>
            </div>
        </div>
      <TabsContent value="experiments">
        <div className="overflow-x-auto border rounded-lg h-[calc(100vh-16rem)]">
          <div style={{ minWidth: `${350 + 150 * allMetrics.length + 100 * 4}px` }}>
            {/* Cabeçalho Fixo */}
            <div className="grid gap-4 px-4 py-2 text-xs font-semibold text-muted-foreground border-b bg-muted/50 sticky top-0"
                 style={{ gridTemplateColumns: `minmax(350px, 1.5fr) repeat(${allMetrics.length}, 150px) repeat(4, 100px)` }}>
              <div className="text-left">Experimento</div>
              {allMetrics.map(metric => (
                <div key={metric} className="text-center">{metric}</div>
              ))}
              <div className="text-center">Duração Total</div>
              <div className="text-center">Total Runs</div>
              <div className="text-center">Sucesso</div>
              <div className="text-center">Falhas</div>
            </div>

            <Accordion type="multiple" className="w-full">
              {filteredAndSortedExperiments.map((exp) => (
                <AccordionItem value={exp.experiment_id} key={exp.experiment_id} className="border-b last:border-b-0">
                  <AccordionTrigger className="hover:no-underline p-3 rounded-none hover:bg-muted/50">
                    <div className="grid gap-4 w-full items-start"
                         style={{ gridTemplateColumns: `minmax(350px, 1.5fr) repeat(${allMetrics.length}, 150px) repeat(4, 100px)` }}>
                      <div className="text-left">
                        <Link href={`/experiments/${datasetId}/${exp.experiment_id}`} className="font-semibold text-primary hover:underline" onClick={(e) => e.stopPropagation()}>
                          {exp.experiment_name}
                        </Link>
                        <p className="text-xs text-muted-foreground mt-1 break-words whitespace-normal">{exp.experiment_description}</p>
                        <p className="text-xs text-muted-foreground mt-2">{new Date(exp.experiment_timestamp).toLocaleString('pt-BR')}</p>
                      </div>
                      {allMetrics.map(metric => {
                        const metricData = exp.aggregate_metrics.find(m => m.metric_name === metric);
                        const score = metricData?.score_statistics?.average ?? null;
                        return (
                          <div key={metric} className="col-span-1 text-center self-center">
                            <ProgressBar score={score} metricName={metric} />
                          </div>
                        );
                      })}
                      <div className="text-center font-semibold self-center">{exp.execution_summary.total_duration_seconds.toFixed(2)}s</div>
                      <div className="text-center font-semibold self-center">{exp.aggregate_metrics[0]?.total_runs || 0}</div>
                      <div className="text-center font-semibold text-green-600 self-center">{exp.aggregate_metrics[0]?.successful_runs || 0}</div>
                      <div className="text-center font-semibold text-red-600 self-center">{exp.error_summary.total_failed_runs}</div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent className="p-6 bg-muted/30">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {exp.aggregate_metrics.map(metric => (
                        <div key={metric.metric_name} className="space-y-3">
                          <h4 className="font-semibold text-base">{metric.metric_name}</h4>
                          <div className="text-xs text-muted-foreground grid grid-cols-2 gap-x-4 gap-y-1">
                            <span>Média: <strong className="text-foreground">{metric.score_statistics?.average?.toFixed(3) ?? 'N/A'}</strong></span>
                            <span>Mediana: <strong className="text-foreground">{metric.score_statistics?.median?.toFixed(3) ?? 'N/A'}</strong></span>
                            <span>Mínimo: <strong className="text-foreground">{metric.score_statistics?.min?.toFixed(3) ?? 'N/A'}</strong></span>
                            <span>Máximo: <strong className="text-foreground">{metric.score_statistics?.max?.toFixed(3) ?? 'N/A'}</strong></span>
                            <span>Desvio Padrão: <strong className="text-foreground">{metric.score_statistics?.std_dev?.toFixed(3) ?? 'N/A'}</strong></span>
                            <span>Duração Média: <strong className="text-foreground">{metric.duration_statistics_seconds?.average?.toFixed(2) ?? 'N/A'}s</strong></span>
                            <span>Sucessos: <strong className="text-foreground text-green-600">{metric.successful_runs}</strong></span>
                            <span>Falhas: <strong className="text-foreground text-red-600">{metric.failed_runs}</strong></span>
                          </div>
                          <div>
                            <h5 className="text-sm font-medium mb-2">Distribuição de Scores</h5>
                            <div className="space-y-1">
                              {metric.score_distribution.map(dist => (
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
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>
        </div>
      </TabsContent>
      <TabsContent value="examples">
        <div className="overflow-auto h-[calc(100vh-16rem)] border rounded-lg">
            <Table>
              <TableHeader className="sticky top-0 bg-background z-10">
                <TableRow>
                  <TableHead className="w-[200px]">ID</TableHead>
                  <TableHead>Prompt</TableHead>
                  <TableHead>Outros Dados</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredExamples.map((ex) => {
                    const { id, prompt, ...rest } = ex;
                    return (
                      <TableRow key={id}>
                        <TableCell className="font-mono text-xs text-muted-foreground">{id}</TableCell>
                        <TableCell className="font-mono text-xs">{prompt}</TableCell>
                        <TableCell>
                          <pre className="text-xs bg-muted rounded-md p-3 whitespace-pre-wrap break-all font-mono">
                            {formatObjectForDisplay(rest)}
                          </pre>
                        </TableCell>
                      </TableRow>
                    )
                })}
              </TableBody>
            </Table>
        </div>
      </TabsContent>
    </Tabs>
  );
}
