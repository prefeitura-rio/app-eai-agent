'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Experiment, Example } from '@/app/components/types';
import sharedStyles from '../page.module.css';
import pageStyles from '../[dataset_id]/page.module.css';
import ProgressBar from './ProgressBar';

interface DatasetExperimentsClientProps {
  experiments: Experiment[];
  examples: Example[];
  datasetId: string;
  datasetName: string;
}

type SortKey = keyof Experiment | 'metric';

export default function DatasetExperimentsClient({ experiments: initialExperiments, examples: initialExamples, datasetId }: DatasetExperimentsClientProps) {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'experiments' | 'examples'>('experiments');
  
  const [experiments] = useState<Experiment[]>(initialExperiments);
  const [expSearchTerm, setExpSearchTerm] = useState('');
  const [expSortConfig, setExpSortConfig] = useState<{ key: SortKey | null; direction: 'ascending' | 'descending'; metricName?: string }>({ key: 'createdAt', direction: 'descending' });

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
  }

  return (
    <div className={sharedStyles.container}>
      <ul className={`nav nav-tabs ${pageStyles.navTabs}`} role="tablist">
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === 'experiments' ? 'active' : ''}`}
            onClick={() => setActiveTab('experiments')}
          >
            Experimentos ({filteredAndSortedExperiments.length})
          </button>
        </li>
        <li className="nav-item" role="presentation">
          <button
            className={`nav-link ${activeTab === 'examples' ? 'active' : ''}`}
            onClick={() => setActiveTab('examples')}
          >
            Exemplos ({filteredExamples.length})
          </button>
        </li>
      </ul>

      <div className="tab-content">
        {/* Experiments Tab Pane */}
        <div className={`tab-pane fade ${activeTab === 'experiments' ? 'show active' : ''}`}>
          <div className={`${sharedStyles.card} ${pageStyles.tabCard}`}>
            <div className={sharedStyles.cardHeader}>
              <div className={sharedStyles.headerLeft}>
                <h5 className={sharedStyles.cardTitle}>Experimentos</h5>
                <div className={sharedStyles.search_container}>
                  <i className="bi bi-search"></i>
                  <input
                    type="text"
                    className="form-control"
                    placeholder="Filtrar por nome..."
                    onChange={(e) => setExpSearchTerm(e.target.value)}
                  />
                </div>
              </div>
              <button className={sharedStyles.actionButton} title="Download CSV">
                <i className="bi bi-download"></i>
              </button>
            </div>
            <div className={`card-body p-0 ${sharedStyles.table_responsive}`}>
              <table className={`table table-hover ${sharedStyles.table}`}>
                <thead className="table-light">
                  <tr>
                    <th onClick={() => requestExpSort('name')} className={`${sharedStyles.sortable_header} ${sharedStyles.textAlignLeft}`}>Nome{getSortIndicator('name')}</th>
                    <th onClick={() => requestExpSort('description')} className={`${sharedStyles.sortable_header} ${sharedStyles.textAlignLeft}`}>Descrição{getSortIndicator('description')}</th>
                    <th onClick={() => requestExpSort('createdAt')} className={`${sharedStyles.sortable_header} ${sharedStyles.textAlignCenter}`}>Criado em{getSortIndicator('createdAt')}</th>
                    {allMetrics.map(metric => (
                      <th key={metric} onClick={() => requestExpSort('metric', metric)} className={`${sharedStyles.sortable_header} ${sharedStyles.textAlignCenter}`}>{metric}{getSortIndicator('metric', metric)}</th>
                    ))}
                    <th onClick={() => requestExpSort('runCount')} className={`${sharedStyles.sortable_header} ${sharedStyles.textAlignCenter}`}>Execuções{getSortIndicator('runCount')}</th>
                    <th onClick={() => requestExpSort('averageRunLatencyMs')} className={`${sharedStyles.sortable_header} ${sharedStyles.textAlignCenter}`}>Latência{getSortIndicator('averageRunLatencyMs')}</th>
                    <th onClick={() => requestExpSort('errorRate')} className={`${sharedStyles.sortable_header} ${sharedStyles.textAlignCenter}`}>Erro{getSortIndicator('errorRate')}</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAndSortedExperiments.map((exp) => (
                    <tr key={exp.id} onClick={() => handleExpRowClick(exp.id)}>
                      <td className={sharedStyles.textAlignLeft}>
                        <Link href={`/experiments/${datasetId}/${exp.id}`} onClick={(e) => e.stopPropagation()} className={sharedStyles.link}>
                          #{exp.sequenceNumber} {exp.name}
                        </Link>
                      </td>
                      <td className={sharedStyles.textAlignLeft}>{exp.description || 'Sem descrição'}</td>
                      <td className={sharedStyles.textAlignCenter}>{new Date(exp.createdAt).toLocaleString('pt-BR')}</td>
                      {allMetrics.map(metric => {
                        const ann = exp.annotationSummaries.find(a => a.annotationName === metric);
                        return <td key={metric} className={sharedStyles.textAlignCenter}><ProgressBar score={ann ? ann.meanScore : 0} /></td>
                      })}
                      <td className={sharedStyles.textAlignCenter}>{exp.runCount}</td>
                      <td className={sharedStyles.textAlignCenter}>{exp.averageRunLatencyMs?.toFixed(2)}ms</td>
                      <td className={sharedStyles.textAlignCenter}>{(exp.errorRate * 100).toFixed(2)}%</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Examples Tab Pane */}
        <div className={`tab-pane fade ${activeTab === 'examples' ? 'show active' : ''}`}>
          <div className={`${sharedStyles.card} ${pageStyles.tabCard}`}>
            <div className={sharedStyles.cardHeader}>
                <div className={sharedStyles.headerLeft}>
                    <h5 className={sharedStyles.cardTitle}>Exemplos</h5>
                    <div className={sharedStyles.search_container}>
                        <i className="bi bi-search"></i>
                        <input
                            type="text"
                            className="form-control"
                            placeholder="Filtrar por conteúdo..."
                            onChange={(e) => setExSearchTerm(e.target.value)}
                        />
                    </div>
                </div>
                <button className={sharedStyles.actionButton} title="Download CSV">
                    <i className="bi bi-download"></i>
                </button>
            </div>
            <div className={`card-body p-0 ${sharedStyles.table_responsive}`}>
              <table className={`table table-hover ${sharedStyles.table}`} style={{ tableLayout: 'fixed' }}>
                <thead className="table-light">
                  <tr>
                    <th className={sharedStyles.textAlignLeft}>ID</th>
                    <th className={sharedStyles.textAlignLeft}>Input</th>
                    <th className={sharedStyles.textAlignLeft}>Output</th>
                    <th className={sharedStyles.textAlignLeft}>Metadata</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredExamples.map((ex) => (
                    <tr key={ex.id}>
                      <td className={sharedStyles.textAlignLeft}>{ex.id}</td>
                      <td className={sharedStyles.textAlignLeft}><pre>{formatObjectForDisplay(ex.latestRevision.input)}</pre></td>
                      <td className={sharedStyles.textAlignLeft}><pre>{formatObjectForDisplay(ex.latestRevision.output)}</pre></td>
                      <td className={sharedStyles.textAlignLeft}><pre>{formatObjectForDisplay(ex.latestRevision.metadata)}</pre></td>
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