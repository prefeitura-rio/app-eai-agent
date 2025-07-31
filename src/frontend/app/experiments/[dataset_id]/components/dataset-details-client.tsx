'use client';

import React, { useState, useMemo, useEffect } from 'react';
import { useRouter } from 'next/navigation';
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
        <div className="overflow-auto h-[calc(100vh-16rem)] border rounded-lg">
            <Table>
              <TableHeader className="sticky top-0 bg-background z-10">
                <TableRow>
                  <SortableHeader sortKey="experiment_name" className="w-[300px]">Nome</SortableHeader>
                  <SortableHeader sortKey="experiment_description">Descrição</SortableHeader>
                  <SortableHeader sortKey="experiment_timestamp" className="text-center w-[180px]">Data</SortableHeader>
                  {allMetrics.map(metric => (
                    <TableHead key={metric} className="text-center w-[150px]">{metric}</TableHead>
                  ))}
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredAndSortedExperiments.map((exp) => (
                  <TableRow key={exp.experiment_id} onClick={() => handleRowClick(exp.experiment_id)} className="cursor-pointer">
                    <TableCell>
                      <Link href={`/experiments/${datasetId}/${exp.experiment_id}`} onClick={(e) => e.stopPropagation()} className="font-medium text-primary hover:underline">
                        {exp.experiment_name}
                      </Link>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{exp.experiment_description || '—'}</TableCell>
                    <TableCell className="text-center text-muted-foreground text-xs">
                        <div>{new Date(exp.experiment_timestamp).toLocaleDateString('pt-BR')}</div>
                        <div>{new Date(exp.experiment_timestamp).toLocaleTimeString('pt-BR')}</div>
                    </TableCell>
                    {allMetrics.map(metric => {
                      const metricData = exp.aggregate_metrics.find(m => m.metric_name === metric);
                      const score = metricData?.score_statistics?.average;
                      return (
                        <TableCell key={metric} className="text-center">
                          <ProgressBar score={score} metricName={metric} />
                        </TableCell>
                      );
                    })}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
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
