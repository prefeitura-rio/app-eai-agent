'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Experiment, Example } from '@/app/components/types';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
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
  datasetId 
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
        let aValue: string | number, bValue: string | number;
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

  const getSortIndicator = (key: SortKey, metricName?: string) => {
    const currentSortKey = metricName ? `metric-${metricName}` : key;
    const prevSortKey = expSortConfig.metricName ? `metric-${expSortConfig.metricName}` : expSortConfig.key;
    if (currentSortKey !== prevSortKey) return null;
    return expSortConfig.direction === 'ascending' ? ' ▲' : ' ▼';
  };
  
  const handleExpRowClick = (experimentId: string) => {
    router.push(`/experiments/${datasetId}/${experimentId}`);
  };

  const formatObjectForDisplay = (obj: Record<string, unknown>) => {
    if (!obj) return '';
    return JSON.stringify(obj, null, 2);
  };

  return (
    <Tabs defaultValue="experiments" className="w-full">
      <TabsList className="grid w-full grid-cols-2">
        <TabsTrigger value="experiments">Experimentos ({filteredAndSortedExperiments.length})</TabsTrigger>
        <TabsTrigger value="examples">Exemplos ({filteredExamples.length})</TabsTrigger>
      </TabsList>
      <TabsContent value="experiments">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Experimentos</CardTitle>
                <CardDescription>Lista de experimentos realizados neste dataset.</CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Input
                  type="text"
                  placeholder="Filtrar por nome..."
                  value={expSearchTerm}
                  onChange={(e) => setExpSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Button variant="outline" size="icon" title="Download CSV">
                  <i className="bi bi-download"></i>
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead onClick={() => requestExpSort('name')}>Nome{getSortIndicator('name')}</TableHead>
                  <TableHead onClick={() => requestExpSort('description')}>Descrição{getSortIndicator('description')}</TableHead>
                  <TableHead onClick={() => requestExpSort('createdAt')} className="text-center">Criado em{getSortIndicator('createdAt')}</TableHead>
                  {allMetrics.map(metric => (
                    <TableHead key={metric} onClick={() => requestExpSort('metric', metric)} className="text-center">
                      {metric}{getSortIndicator('metric', metric)}
                    </TableHead>
                  ))}
                  <TableHead onClick={() => requestExpSort('runCount')} className="text-center">Execuções{getSortIndicator('runCount')}</TableHead>
                  <TableHead onClick={() => requestExpSort('errorRate')} className="text-center">Erro{getSortIndicator('errorRate')}</TableHead>
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
                    <TableCell>{exp.description || 'Sem descrição'}</TableCell>
                    <TableCell className="text-center">{new Date(exp.createdAt).toLocaleString('pt-BR')}</TableCell>
                    {allMetrics.map(metric => {
                      const ann = exp.annotationSummaries.find(a => a.annotationName === metric);
                      return (
                        <TableCell key={metric} className="text-center">
                          <ProgressBar score={ann ? ann.meanScore : 0} metricName={metric} />
                        </TableCell>
                      );
                    })}
                    <TableCell className="text-center">{exp.runCount}</TableCell>
                    <TableCell className="text-center">{(exp.errorRate * 100).toFixed(2)}%</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </TabsContent>
      <TabsContent value="examples">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Exemplos</CardTitle>
                <CardDescription>Exemplos de dados de entrada e saída para este dataset.</CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Input
                  type="text"
                  placeholder="Filtrar por conteúdo..."
                  value={exSearchTerm}
                  onChange={(e) => setExSearchTerm(e.target.value)}
                  className="w-64"
                />
                <Button variant="outline" size="icon" title="Download CSV">
                  <i className="bi bi-download"></i>
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead style={{ width: '200px' }}>ID</TableHead>
                  <TableHead style={{ width: '300px' }}>Input</TableHead>
                  <TableHead style={{ width: '300px' }}>Output</TableHead>
                  <TableHead>Metadata</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredExamples.map((ex) => (
                  <TableRow key={ex.id}>
                    <TableCell className="font-mono text-xs">{ex.id}</TableCell>
                    <TableCell>
                      <pre className="text-xs bg-muted text-muted-foreground p-2 rounded-md whitespace-pre-wrap break-all">
                        {formatObjectForDisplay(ex.latestRevision.input)}
                      </pre>
                    </TableCell>
                    <TableCell>
                      <pre className="text-xs bg-muted text-muted-foreground p-2 rounded-md whitespace-pre-wrap break-all">
                        {formatObjectForDisplay(ex.latestRevision.output)}
                      </pre>
                    </TableCell>
                    <TableCell>
                      <pre className="text-xs bg-muted text-muted-foreground p-2 rounded-md whitespace-pre-wrap break-all">
                        {formatObjectForDisplay(ex.latestRevision.metadata)}
                      </pre>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}