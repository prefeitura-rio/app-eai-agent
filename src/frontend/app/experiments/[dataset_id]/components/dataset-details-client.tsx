'use client';

import React, { useState, useMemo, useEffect } from 'react';
import Link from 'next/link';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger, TooltipProvider } from '@/components/ui/tooltip';
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
import { Search, RefreshCw, Trash2, ArrowUp, ArrowDown } from 'lucide-react';
import { useHeader } from '@/app/contexts/HeaderContext';
import { useAuth } from '@/app/contexts/AuthContext';
import { DatasetExperimentInfo, DatasetExample } from '../../types';
import { deleteExperiment } from '../../services/api';
import { toast } from 'sonner';
import ColumnsSelector from './ColumnsSelector';
import CompactMetricCell from './CompactMetricCell';

interface ClientProps {
  experiments: DatasetExperimentInfo[];
  examples: DatasetExample[];
  datasetId: string;
  datasetName: string;
}

type SortDirection = 'asc' | 'desc' | null;

interface SortConfig {
  key: string;
  direction: SortDirection;
}

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
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'experiment_timestamp', direction: 'desc' });
  const [isDeleting, setIsDeleting] = useState<string | null>(null);

  // Get all unique metric names
  const allMetrics = useMemo(() => {
    const metrics = new Set<string>();
    experiments.forEach(exp => {
      exp.aggregate_metrics.forEach(metric => metrics.add(metric.metric_name));
    });
    return Array.from(metrics).sort();
  }, [experiments]);

  // State for visible columns (default to all)
  const [visibleColumns, setVisibleColumns] = useState<string[]>(allMetrics);

  // Update visible columns when allMetrics changes (but preserve user selection)
  useEffect(() => {
    if (visibleColumns.length === 0 && allMetrics.length > 0) {
      setVisibleColumns(allMetrics);
    }
  }, [allMetrics, visibleColumns.length]);

  useEffect(() => {
    setTitle('Experimentos do Dataset');
    setSubtitle(datasetName);
  }, [setTitle, setSubtitle, datasetName]);

  useEffect(() => {
    setExperiments(initialExperiments);
  }, [initialExperiments]);

  // Filter and sort experiments
  const filteredAndSortedExperiments = useMemo(() => {
    let result = [...experiments];
    
    // Filter by search term
    if (searchTerm) {
      result = result.filter(item =>
        item.experiment_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.experiment_description?.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Sort
    if (sortConfig.key && sortConfig.direction) {
      result.sort((a, b) => {
        let aValue: number | string;
        let bValue: number | string;
        
        // Check if sorting by a metric
        if (allMetrics.includes(sortConfig.key)) {
          const aMetric = a.aggregate_metrics.find(m => m.metric_name === sortConfig.key);
          const bMetric = b.aggregate_metrics.find(m => m.metric_name === sortConfig.key);
          aValue = aMetric?.score_statistics?.average ?? -1;
          bValue = bMetric?.score_statistics?.average ?? -1;
        } else {
          // Sort by standard fields
          switch (sortConfig.key) {
            case 'experiment_timestamp':
              aValue = new Date(a.experiment_timestamp).getTime();
              bValue = new Date(b.experiment_timestamp).getTime();
              break;
            case 'experiment_name':
              aValue = a.experiment_name.toLowerCase();
              bValue = b.experiment_name.toLowerCase();
              break;
            case 'total_runs':
              aValue = a.aggregate_metrics[0]?.total_runs || 0;
              bValue = b.aggregate_metrics[0]?.total_runs || 0;
              break;
            case 'duration':
              aValue = a.execution_summary.total_duration_seconds;
              bValue = b.execution_summary.total_duration_seconds;
              break;
            default:
              aValue = 0;
              bValue = 0;
          }
        }
        
        if (aValue < bValue) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aValue > bValue) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    
    return result;
  }, [experiments, searchTerm, sortConfig, allMetrics]);

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

  const handleSort = (key: string) => {
    setSortConfig(prev => {
      if (prev.key !== key) {
        return { key, direction: 'desc' };
      }
      if (prev.direction === 'desc') {
        return { key, direction: 'asc' };
      }
      if (prev.direction === 'asc') {
        return { key: 'experiment_timestamp', direction: 'desc' };
      }
      return { key, direction: 'desc' };
    });
  };

  const getSortIcon = (key: string) => {
    if (sortConfig.key !== key) {
      return null;
    }
    if (sortConfig.direction === 'asc') {
      return <ArrowUp className="h-3 w-3 ml-1" />;
    }
    return <ArrowDown className="h-3 w-3 ml-1" />;
  };

  const handleDeleteExperiment = async (experimentId: string, experimentName: string) => {
    if (isDeleting === experimentId || !token) return;
    
    setIsDeleting(experimentId);
    
    try {
      await deleteExperiment(experimentId, datasetId, token);
      setExperiments(prev => prev.filter(exp => exp.experiment_id !== experimentId));
      toast.success(`Experimento "${experimentName}" deletado com sucesso!`);
    } catch (error) {
      console.error('Error deleting experiment:', error);
      toast.error(`Erro ao deletar experimento "${experimentName}": ${error instanceof Error ? error.message : 'Erro desconhecido'}`);
    } finally {
      setIsDeleting(null);
    }
  };

  // Only show visible metrics
  const displayMetrics = useMemo(() => 
    allMetrics.filter(m => visibleColumns.includes(m)),
    [allMetrics, visibleColumns]
  );

  return (
    <TooltipProvider>
      <Tabs defaultValue="experiments" className="w-full space-y-4">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="experiments">Experimentos ({filteredAndSortedExperiments.length})</TabsTrigger>
            <TabsTrigger value="examples">Exemplos ({filteredExamples.length})</TabsTrigger>
          </TabsList>
          <div className="flex items-center gap-2">
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
            <ColumnsSelector
              availableColumns={allMetrics}
              selectedColumns={visibleColumns}
              onSelectionChange={setVisibleColumns}
            />
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
          <div className="border rounded-lg overflow-auto h-[calc(100vh-12rem)]">
              <Table>
                <TableHeader className="sticky top-0 bg-background z-10">
                  <TableRow>
                    {/* Fixed experiment column */}
                    <TableHead 
                      className="min-w-[300px] max-w-[400px] cursor-pointer hover:bg-muted/50 sticky left-0 bg-background z-20"
                      onClick={() => handleSort('experiment_name')}
                    >
                      <div className="flex items-center">
                        Experimento
                        {getSortIcon('experiment_name')}
                      </div>
                    </TableHead>
                    
                    {/* Metric columns */}
                    {displayMetrics.map(metric => (
                      <TableHead 
                        key={metric} 
                        className="text-center min-w-[120px] max-w-[150px] cursor-pointer hover:bg-muted/50 align-bottom"
                        onClick={() => handleSort(metric)}
                      >
                        <div className="flex flex-col items-center justify-end gap-1 py-2">
                          <span className="text-xs leading-tight text-center whitespace-normal break-words">{metric}</span>
                          {getSortIcon(metric)}
                        </div>
                      </TableHead>
                    ))}
                    
                    {/* Fixed info columns */}
                    <TableHead 
                      className="text-center min-w-[80px] cursor-pointer hover:bg-muted/50"
                      onClick={() => handleSort('duration')}
                    >
                      <div className="flex items-center justify-center">
                        Duração
                        {getSortIcon('duration')}
                      </div>
                    </TableHead>
                    <TableHead 
                      className="text-center min-w-[70px] cursor-pointer hover:bg-muted/50"
                      onClick={() => handleSort('total_runs')}
                    >
                      <div className="flex items-center justify-center">
                        Runs
                        {getSortIcon('total_runs')}
                      </div>
                    </TableHead>
                    <TableHead className="text-center min-w-[50px]">OK</TableHead>
                    <TableHead className="text-center min-w-[50px]">Err</TableHead>
                    <TableHead className="w-[50px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredAndSortedExperiments.map((exp) => (
                    <TableRow 
                      key={exp.experiment_id} 
                      className="hover:bg-muted/30 transition-colors"
                    >
                      {/* Experiment info */}
                      <TableCell className="min-w-[300px] max-w-[400px] sticky left-0 bg-background">
                        <div className="space-y-1">
                          <Link 
                            href={`/experiments/${datasetId}/${exp.experiment_id}`} 
                            className="font-semibold text-primary hover:underline block"
                          >
                            {exp.experiment_name}
                          </Link>
                          {exp.experiment_description && (
                            <p className="text-xs text-muted-foreground line-clamp-2">
                              {exp.experiment_description}
                            </p>
                          )}
                          <p className="text-xs text-muted-foreground">
                            {new Date(exp.experiment_timestamp).toLocaleString('pt-BR')}
                          </p>
                        </div>
                      </TableCell>
                      
                      {/* Metric cells */}
                      {displayMetrics.map(metric => {
                        const metricData = exp.aggregate_metrics.find(m => m.metric_name === metric);
                        const score = metricData?.score_statistics?.average ?? null;
                        return (
                          <TableCell key={metric} className="text-center p-1">
                            <CompactMetricCell score={score} />
                          </TableCell>
                        );
                      })}
                      
                      {/* Info columns */}
                      <TableCell className="text-center text-sm">
                        {exp.execution_summary.total_duration_seconds.toFixed(1)}s
                      </TableCell>
                      <TableCell className="text-center text-sm font-medium">
                        {exp.aggregate_metrics[0]?.total_runs || 0}
                      </TableCell>
                      <TableCell className="text-center text-sm font-medium text-green-600">
                        {exp.aggregate_metrics[0]?.successful_runs || 0}
                      </TableCell>
                      <TableCell className="text-center text-sm font-medium text-red-600">
                        {Number(exp.error_summary.total_failed_runs) || 0}
                      </TableCell>
                      
                      {/* Delete button */}
                      <TableCell className="p-1">
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-7 w-7 text-muted-foreground hover:text-red-600 hover:bg-red-50"
                              disabled={isDeleting === exp.experiment_id}
                            >
                              {isDeleting === exp.experiment_id ? (
                                <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                              ) : (
                                <Trash2 className="h-3.5 w-3.5" />
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
                                Deletar
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
          </div>
        </TabsContent>

        <TabsContent value="examples">
          <div className="overflow-auto h-[calc(100vh-12rem)] border rounded-lg">
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
                  );
                })}
              </TableBody>
            </Table>
          </div>
        </TabsContent>
      </Tabs>
    </TooltipProvider>
  );
}
