'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { Experiment, Example } from '@/app/components/types';
import styles from '../[dataset_id]/page.module.css';
import ProgressBar from './ProgressBar';

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
  const [experiments, setExperiments] = useState<Experiment[]>(initialExperiments);
  const [expSearchTerm, setExpSearchTerm] = useState('');
  const [expSortConfig, setExpSortConfig] = useState<{ key: SortKey | null; direction: 'ascending' | 'descending'; metricName?: string }>({ key: 'createdAt', direction: 'descending' });

  // Examples state
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

    // Define which keys of Experiment are sortable
    type SortableExperimentKeys = 'name' | 'description' | 'createdAt' | 'runCount' | 'averageRunLatencyMs' | 'errorRate' | 'sequenceNumber';

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
            // Ensure we only access sortable keys
            const key = expSortConfig.key as SortableExperimentKeys;
            aValue = a[key];
            bValue = b[key];
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
      <ul className="nav nav-tabs" id="datasetTabs" role="tablist">
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === 'experiments' ? 'active' : ''}`}
            onClick={() => setActiveTab('experiments')}
            type="button"
          >
            Experimentos ({filteredAndSortedExperiments.length})
          </button>
        </li>
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === 'examples' ? 'active' : ''}`}
            onClick={() => setActiveTab('examples')}
            type="button"
          >
            Exemplos ({filteredExamples.length})
          </button>
        </li>
      </ul>

      <div className="tab-content" id="datasetTabContent">
        <div className={`tab-pane fade ${activeTab === 'experiments' ? 'show active' : ''}`}>
          <div className={styles.card}>
            <div className="card-header">
              <div className="d-flex align-items-center gap-3">
                <h5 className="mb-0">Experimentos</h5>
                <span className="text-muted">|</span>
                <div className={styles.search_container}>
                  <i className="bi bi-search text-muted"></i>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Filtrar por nome do experimento..."
                    style={{ width: '250px' }}
                    onChange={(e) => setExpSearchTerm(e.target.value)}
                  />
                </div>
                <button className="btn btn-sm btn-outline-success">
                  <i className="bi bi-download me-1"></i>CSV
                </button>
              </div>
            </div>
            <div className={`card-body p-0 ${styles.table_responsive}`}>
              <table className={`table table-hover ${styles.table}`}>
                <thead className="table-light">
                  <tr>
                    <th onClick={() => requestExpSort('name')}>Nome</th>
                    <th onClick={() => requestExpSort('description')}>Descrição</th>
                    <th onClick={() => requestExpSort('createdAt')}>Criado em</th>
                    {allMetrics.map(metric => (
                      <th key={metric} onClick={() => requestExpSort('metric', metric)}>{metric}</th>
                    ))}
                    <th onClick={() => requestExpSort('runCount')}>Execuções</th>
                    <th onClick={() => requestExpSort('averageRunLatencyMs')}>Latência</th>
                    <th onClick={() => requestExpSort('errorRate')}>Erro</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAndSortedExperiments.map((exp) => (
                    <tr key={exp.id} onClick={() => handleExpRowClick(exp.id)}>
                      <td>#{exp.sequenceNumber} {exp.name}</td>
                      <td>{exp.description || 'Sem descrição'}</td>
                      <td>{new Date(exp.createdAt).toLocaleString('pt-BR')}</td>
                      {allMetrics.map(metric => {
                        const ann = exp.annotationSummaries.find(a => a.annotationName === metric);
                        const score = ann ? ann.meanScore : 0;
                        return <td key={metric}><ProgressBar score={score} metricName={metric} /></td>
                      })}
                      <td>{exp.runCount}</td>
                      <td>{exp.averageRunLatencyMs?.toFixed(2)}ms</td>
                      <td>{(exp.errorRate * 100).toFixed(2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <div className={`tab-pane fade ${activeTab === 'examples' ? 'show active' : ''}`}>
          <div className={styles.card}>
            <div className="card-header">
              <div className="d-flex align-items-center gap-3">
                <h5 className="mb-0">Examples</h5>
                <span className="text-muted">|</span>
                <div className={styles.search_container}>
                  <i className="bi bi-search text-muted"></i>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Filtrar por conteúdo do exemplo..."
                    style={{ width: '250px' }}
                    onChange={(e) => setExSearchTerm(e.target.value)}
                  />
                </div>
                <button className="btn btn-sm btn-outline-success">
                  <i className="bi bi-download me-1"></i>CSV
                </button>
              </div>
            </div>
            <div className={`card-body p-0 ${styles.table_responsive}`}>
              <table className={`table table-hover ${styles.table}`} style={{ tableLayout: 'fixed' }}>
                <thead className="table-light">
                  <tr>
                    <th>ID</th>
                    <th>Input</th>
                    <th>Output</th>
                    <th>Metadata</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredExamples.map((ex) => (
                    <tr key={ex.id}>
                      <td>{ex.id}</td>
                      <td><pre>{formatObjectForDisplay(ex.latestRevision.input)}</pre></td>
                      <td><pre>{formatObjectForDisplay(ex.latestRevision.output)}</pre></td>
                      <td><pre>{formatObjectForDisplay(ex.latestRevision.metadata)}</pre></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}