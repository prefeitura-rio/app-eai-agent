'use client';

import React, { useState, useMemo, useEffect } from 'react';
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
  Accordion,
  AccordionContent,
  AccordionItem,
} from "@/components/ui/accordion";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import ProgressBar from './ProgressBar';
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { Search, RefreshCw, Trash2 } from 'lucide-react';
import { useHeader } from '@/app/contexts/HeaderContext';
import { useAuth } from '@/app/contexts/AuthContext';
import { DatasetExperimentInfo, DatasetExample } from '../../types';
import { deleteExperiment } from '../../services/api';
import { toast } from 'sonner';

interface ClientProps {
  experiments: DatasetExperimentInfo[];
  examples: DatasetExample[];
  datasetId: string;
  datasetName: string;
}

type SortKey = keyof DatasetExperimentInfo;

export default function DatasetDetailsClient({ 
  experiments: initialExperiments, 
  examples: initialExamples, 
  datasetId,
  datasetName
}: ClientProps) {
  const { setTitle, setSubtitle } = useHeader();
  const { token } = useAuth();
  
  const [experiments, setExperiments] = useState<DatasetExperimentInfo[]>(initialExperiments);
  const [examples] = useState<DatasetExample[]>(initialExamples);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig] = useState<{ key: SortKey | null; direction: 'ascending' | 'descending' }>({ key: 'experiment_timestamp', direction: 'descending' });
  const [isDeleting, setIsDeleting] = useState<string | null>(null);

  useEffect(() => {
    setTitle('Experimentos do Dataset');
    setSubtitle(datasetName);
  }, [setTitle, setSubtitle, datasetName]);

  useEffect(() => {
    setExperiments(initialExperiments);
  }, [initialExperiments]);

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

  const formatObjectForDisplay = (obj: Record<string, unknown>) => {
    if (!obj) return '';
    return JSON.stringify(obj, null, 2);
  };

  const handleDeleteExperiment = async (experimentId: string, experimentName: string) => {
    if (isDeleting === experimentId || !token) return;
    
    setIsDeleting(experimentId);
    
    try {
      await deleteExperiment(experimentId, datasetId, token);
      
      // Remove the experiment from the local state
      setExperiments(prev => prev.filter(exp => exp.experiment_id !== experimentId));
      
      toast.success(`Experimento "${experimentName}" deletado com sucesso!`);
    } catch (error) {
      console.error('Error deleting experiment:', error);
      toast.error(`Erro ao deletar experimento "${experimentName}": ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    } finally {
      setIsDeleting(null);
    }
  };

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
                  <div className="grid gap-4 w-full items-start p-3 hover:bg-muted/50"
                       style={{ gridTemplateColumns: `minmax(350px, 1.5fr) repeat(${allMetrics.length}, 150px) repeat(4, 100px)` }}>
                    <div className="text-left flex items-start justify-between">
                      <div className="flex-1">
                        <Link href={`/experiments/${datasetId}/${exp.experiment_id}`} className="font-semibold text-primary hover:underline">
                          {exp.experiment_name}
                        </Link>
                        <p className="text-xs text-muted-foreground mt-1 break-words whitespace-normal">{exp.experiment_description}</p>
                        <p className="text-xs text-muted-foreground mt-2">{new Date(exp.experiment_timestamp).toLocaleString('pt-BR')}</p>
                      </div>
                      <div className="ml-2 flex-shrink-0">
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-red-500 hover:text-red-700 hover:bg-red-50"
                              disabled={isDeleting === exp.experiment_id}
                            >
                              {isDeleting === exp.experiment_id ? (
                                <RefreshCw className="h-4 w-4 animate-spin" />
                              ) : (
                                <Trash2 className="h-4 w-4" />
                              )}
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Confirmar exclusão</AlertDialogTitle>
                              <AlertDialogDescription>
                                Tem certeza que deseja deletar o experimento &quot;{exp.experiment_name}&quot;? 
                                <br /><br />
                                <strong>Esta ação não pode ser desfeita.</strong>
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancelar</AlertDialogCancel>
                              <AlertDialogAction
                                onClick={() => handleDeleteExperiment(exp.experiment_id, exp.experiment_name)}
                                className="bg-red-500 hover:bg-red-600"
                              >
                                Deletar Experimento
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </div>
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
                    <div className="text-center font-semibold text-red-600 self-center">{Number(exp.error_summary.total_failed_runs) || 0}</div>
                  </div>
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
