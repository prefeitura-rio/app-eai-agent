'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { Experiment, Example } from '@/app/components/types';

interface DatasetExperimentsClientProps {
  experiments: Experiment[];
  examples: Example[];
  datasetId: string;
}

type SortKey = keyof Experiment | 'metric';

export default function DatasetExperimentsClient({ experiments: initialExperiments, examples: initialExamples, datasetId }: DatasetExperimentsClientProps) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'experiments' | 'examples'>('experiments');
  
  // Experiments state
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [experiments, setExperiments] = useState<Experiment[]>(initialExperiments);
  const [expSearchTerm, setExpSearchTerm] = useState('');
  const [expSortConfig, setExpSortConfig] = useState<{ key: SortKey | null; direction: 'ascending' | 'descending'; metricName?: string }>({ key: 'createdAt', direction: 'descending' });

  // Examples state
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const [examples, setExamples] = useState<Example[]>(initialExamples);
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

    type SortableExperimentKeys = 'name' | 'description' | 'createdAt' | 'runCount' | 'averageRunLatencyMs' | 'errorRate' | 'sequenceNumber';

// ...

    if (expSortConfig.key) {
      sortableItems.sort((a, b) => {
        let aValue: string | number | null, bValue: string | number | null;

        if (expSortConfig.key === 'metric') {
            const metricName = expSortConfig.metricName!;
            const aAnn = a.annotationSummaries.find(ann => ann.annotationName === metricName);
            const bAnn = b.annotationSummaries.find(ann => ann.annotationName === metricName);
            aValue = aAnn ? aAnn.meanScore : -1;
            bValue = bAnn ? bAnn.meanScore : -1;
        } else {
            aValue = a[expSortConfig.key as SortableExperimentKeys];
            bValue = b[expSortConfig.key as SortableExperimentKeys];
        }

        if (aValue === null) return 1;
        if (bValue === null) return -1;
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
      const input = JSON.stringify(ex.latestRevision.input).toLowerCase();
      const output = JSON.stringify(ex.latestRevision.output).toLowerCase();
      return input.includes(exSearchTerm.toLowerCase()) || output.includes(exSearchTerm.toLowerCase());
    });
  }, [examples, exSearchTerm]);

  const requestExpSort = (key: SortKey, metricName?: string) => {
    let direction: 'ascending' | 'descending' = 'ascending';
    const currentKey = metricName ? `metric-${metricName}` : key;
    const prevKey = expSortConfig.metricName ? `metric-${expSortConfig.metricName}` : expSortConfig.key;

    if (currentKey === prevKey && expSortConfig.direction === 'ascending') {
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
  }

  return (
    <div>
      <div className="border-b border-gray-200 dark:border-gray-700">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            onClick={() => setActiveTab('experiments')}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'experiments' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
          >
            Experimentos ({filteredAndSortedExperiments.length})
          </button>
          <button
            onClick={() => setActiveTab('examples')}
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'examples' ? 'border-indigo-500 text-indigo-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
          >
            Exemplos ({filteredExamples.length})
          </button>
        </nav>
      </div>

      <div className="mt-4">
        {activeTab === 'experiments' && (
          <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg overflow-hidden">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <h2 className="text-xl font-semibold">Experimentos</h2>
              <input
                type="text"
                placeholder="Filtrar por nome..."
                className="px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
                onChange={(e) => setExpSearchTerm(e.target.value)}
              />
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => requestExpSort('name')}>Nome</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => requestExpSort('description')}>Descrição</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => requestExpSort('createdAt')}>Criado em</th>
                    {allMetrics.map(metric => (
                        <th key={metric} scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => requestExpSort('metric', metric)}>{metric}</th>
                    ))}
                    <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => requestExpSort('runCount')}>Execuções</th>
                    <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => requestExpSort('averageRunLatencyMs')}>Latência</th>
                    <th scope="col" className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider cursor-pointer" onClick={() => requestExpSort('errorRate')}>Erro</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredAndSortedExperiments.map((exp) => (
                    <tr key={exp.id} onClick={() => handleExpRowClick(exp.id)} className="hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">#{exp.sequenceNumber} {exp.name}</td>
                      <td className="px-6 py-4 whitespace-normal text-sm text-gray-500 dark:text-gray-300">{exp.description || 'Sem descrição'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{new Date(exp.createdAt).toLocaleString('pt-BR')}</td>
                      {allMetrics.map(metric => {
                          const ann = exp.annotationSummaries.find(a => a.annotationName === metric);
                          const score = ann ? ann.meanScore.toFixed(2) : '-';
                          return <td key={metric} className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500 dark:text-gray-300">{score}</td>
                      })}
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500 dark:text-gray-300">{exp.runCount}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500 dark:text-gray-300">{exp.averageRunLatencyMs?.toFixed(2)}ms</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500 dark:text-gray-300">{(exp.errorRate * 100).toFixed(2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'examples' && (
          <div className="bg-white dark:bg-gray-800 shadow-md rounded-lg overflow-hidden">
             <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <h2 className="text-xl font-semibold">Exemplos</h2>
              <input
                type="text"
                placeholder="Filtrar por conteúdo..."
                className="px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
                onChange={(e) => setExSearchTerm(e.target.value)}
              />
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">ID</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Input</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Output</th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Metadata</th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {filteredExamples.map((ex) => (
                    <tr key={ex.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{ex.id}</td>
                      <td className="px-6 py-4 whitespace-pre-wrap text-sm text-gray-500 dark:text-gray-300 font-mono">{formatObjectForDisplay(ex.latestRevision.input)}</td>
                      <td className="px-6 py-4 whitespace-pre-wrap text-sm text-gray-500 dark:text-gray-300 font-mono">{formatObjectForDisplay(ex.latestRevision.output)}</td>
                      <td className="px-6 py-4 whitespace-pre-wrap text-sm text-gray-500 dark:text-gray-300 font-mono">{formatObjectForDisplay(ex.latestRevision.metadata)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}