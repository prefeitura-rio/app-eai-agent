'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Experiment, Example } from '@/app/components/types';
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
import { Badge } from "@/components/ui/badge";
import ProgressBar from './ProgressBar';
import { Download, Search, ArrowUp, ArrowDown } from 'lucide-react';
import { cn } from '@/app/utils/utils';

interface DatasetExperimentsClientProps {
  experiments: Experiment[];
  examples: Example[];
  datasetId: string;
  datasetName: string;
}

type SortKey = keyof Experiment | 'metric';

export default function DatasetExperimentsClient({ 
  experiments: initialExperiments, 
  examples: initialExamples, 
  datasetId,
  datasetName
}: DatasetExperimentsClientProps) {
  const router = useRouter();
  
  const [experiments] = useState<Experiment[]>(initialExperiments);
  const [expSearchTerm, setExpSearchTerm] = useState('');
  const [expSortConfig, setExpSortConfig] = useState<{ 
    key: SortKey | null; 
    direction: 'ascending' | 'descending'; 
    metricName?: string 
  }>({ key: 'createdAt', direction: 'descending' });

  const [examples] = useState<Example[]>(initialExamples);
  const [exSearchTerm, setExSearchTerm] = useState('');

  const allMetrics = useMemo(() => {
    const metrics = new Set<string>();
    experiments.forEach(exp => {
      exp.annotationSummaries.forEach(ann => metrics.add(ann.annotationName));
    });
    return Array.from(metrics).sort();
  }, [experiments]);

  const filteredAndSortedExperiments = useMemo(() => {
    let sortableItems = [...experiments];
    if (expSearchTerm) {
      sortableItems = sortableItems.filter(item =>
        item.name.toLowerCase().includes(expSearchTerm.toLowerCase())
      );
    }
    if (expSortConfig.key) {
      sortableItems.sort((a, b) => {
        let aValue: any, bValue: any;
        if (expSortConfig.key === 'metric') {
          const metricName = expSortConfig.metricName!;
          aValue = a.annotationSummaries.find(ann => ann.annotationName === metricName)?.meanScore ?? -1;
          bValue = b.annotationSummaries.find(ann => ann.annotationName === metricName)?.meanScore ?? -1;
        } else {
          aValue = a[expSortConfig.key as keyof Experiment];
          bValue = b[expSortConfig.key as keyof Experiment];
        }
        if (aValue < bValue) return expSortConfig.direction === 'ascending' ? -1 : 1;
        if (aValue > bValue) return expSortConfig.direction === 'ascending' ? 1 : -1;
        return 0;
      });
    }
    return sortableItems;
  }, [experiments, expSearchTerm, expSortConfig]);

  const filteredExamples = useMemo(() => {
    if (!exSearchTerm) return examples;
    return examples.filter(ex => {
      const content = JSON.stringify(ex.latestRevision.input) + JSON.stringify(ex.latestRevision.output);
      return content.toLowerCase().includes(exSearchTerm.toLowerCase());
    });
  }, [examples, exSearchTerm]);

  const requestExpSort = (key: SortKey, metricName?: string) => {
    let direction: 'ascending' | 'descending' = 'ascending';
    const currentSortKey = metricName ? `metric-${metricName}` : key;
    const prevSortKey = expSortConfig.metricName ? `metric-${expSortConfig.metricName}` : expSortConfig.key;
    if (currentSortKey === prevSortKey && expSortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setExpSortConfig({ key, direction, metricName });
  };
  
  const handleExpRowClick = (experimentId: string) => {
    router.push(`/experiments/${datasetId}/${experimentId}`);
  };

  const formatObjectForDisplay = (obj: Record<string, unknown>) => {
    if (!obj) return '';
    return JSON.stringify(obj, null, 2);
  };

  const SortableHeader = ({ sortKey, metricName, children, className }: { sortKey: SortKey, metricName?: string, children: React.ReactNode, className?: string }) => {
    const isSorted = expSortConfig.metricName ? expSortConfig.metricName === metricName : expSortConfig.key === sortKey;
    return (
        <TableHead className={className}>
            <Button variant="ghost" onClick={() => requestExpSort(sortKey, metricName)} className="w-full justify-start px-2 text-xs uppercase">
                {children}
                {isSorted && (
                    expSortConfig.direction === 'ascending' ? <ArrowUp className="ml-2 h-4 w-4" /> : <ArrowDown className="ml-2 h-4 w-4" />
                )}
            </Button>
        </TableHead>
    );
  };

  return (
    <Tabs defaultValue="experiments" className="w-full space-y-4">
        <div className="flex items-center justify-between">
            <TabsList>
                <TabsTrigger value="experiments">Experimentos ({filteredAndSortedExperiments.length})</TabsTrigger>
                <TabsTrigger value="examples">Exemplos ({filteredExamples.length})</TabsTrigger>
            </TabsList>
            <div className="flex items-center gap-2">
                <Input
                  type="text"
                  placeholder="Filtrar..."
                  value={expSearchTerm}
                  onChange={(e) => setExpSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Button variant="outline" size="icon" title="Download CSV">
                  <Download className="h-4 w-4" />
                </Button>
            </div>
        </div>
      <TabsContent value="experiments">
        <div className="overflow-y-auto h-[calc(100vh-16rem)] border rounded-lg">
            <Table>
              <TableHeader className="sticky top-0 bg-background">
                <TableRow>
                  <SortableHeader sortKey="name" className="w-[250px]">Nome</SortableHeader>
                  <SortableHeader sortKey="description">Descrição</SortableHeader>
                  <SortableHeader sortKey="createdAt" className="text-center w-[150px]">Criado em</SortableHeader>
                  {allMetrics.map(metric => (
                    <SortableHeader key={metric} sortKey="metric" metricName={metric} className="text-center w-[150px]">
                      {metric}
                    </SortableHeader>
                  ))}
                  <SortableHeader sortKey="runCount" className="text-center w-[120px]">Execuções</SortableHeader>
                  <SortableHeader sortKey="errorRate" className="text-center w-[120px]">Erro</SortableHeader>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredAndSortedExperiments.map((exp) => (
                  <TableRow key={exp.id} onClick={() => handleExpRowClick(exp.id)} className="cursor-pointer">
                    <TableCell>
                      <Link href={`/experiments/${datasetId}/${exp.id}`} onClick={(e) => e.stopPropagation()} className="font-medium text-primary hover:underline">
                        #{exp.sequenceNumber} {exp.name}
                      </Link>
                    </TableCell>
                    <TableCell className="text-muted-foreground">{exp.description || '—'}</TableCell>
                    <TableCell className="text-center text-muted-foreground">{new Date(exp.createdAt).toLocaleDateString('pt-BR')}</TableCell>
                    {allMetrics.map(metric => {
                      const ann = exp.annotationSummaries.find(a => a.annotationName === metric);
                      return (
                        <TableCell key={metric} className="text-center">
                          <ProgressBar score={ann ? ann.meanScore : 0} metricName={metric} />
                        </TableCell>
                      );
                    })}
                    <TableCell className="text-center text-muted-foreground">{exp.runCount}</TableCell>
                    <TableCell className="text-center text-muted-foreground">{(exp.errorRate * 100).toFixed(2)}%</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
        </div>
      </TabsContent>
      <TabsContent value="examples">
        <div className="overflow-y-auto h-[calc(100vh-16rem)] border rounded-lg">
            <Table>
              <TableHeader className="sticky top-0 bg-background">
                <TableRow>
                  <TableHead className="w-[200px]">ID</TableHead>
                  <TableHead>Input</TableHead>
                  <TableHead>Output</TableHead>
                  <TableHead>Metadata</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredExamples.map((ex) => (
                  <TableRow key={ex.id}>
                    <TableCell className="font-mono text-xs text-muted-foreground">{ex.id}</TableCell>
                    <TableCell>
                      <pre className="text-xs bg-muted rounded-md p-3 whitespace-pre-wrap break-all font-mono">
                        {formatObjectForDisplay(ex.latestRevision.input)}
                      </pre>
                    </TableCell>
                    <TableCell>
                      <pre className="text-xs bg-muted rounded-md p-3 whitespace-pre-wrap break-all font-mono">
                        {formatObjectForDisplay(ex.latestRevision.output)}
                      </pre>
                    </TableCell>
                    <TableCell>
                      <pre className="text-xs bg-muted rounded-md p-3 whitespace-pre-wrap break-all font-mono">
                        {formatObjectForDisplay(ex.latestRevision.metadata)}
                      </pre>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
        </div>
      </TabsContent>
    </Tabs>
  );
}
