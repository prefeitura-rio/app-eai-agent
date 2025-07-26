'use client';

import React, { useState, useMemo, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Dataset } from '@/app/components/types';
import { exportToCsv } from '@/app/utils/csv';
import styles from '../page.module.css';

interface DatasetsClientProps {
  datasets: Dataset[];
}

export default function DatasetsClient({ datasets: initialDatasets }: DatasetsClientProps) {
  const router = useRouter();
  const [datasets, setDatasets] = useState<Dataset[]>(initialDatasets);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState<{ key: keyof Dataset | null; direction: 'ascending' | 'descending' }>({ key: 'createdAt', direction: 'descending' });

  useEffect(() => {
    setDatasets(initialDatasets);
  }, [initialDatasets]);

  const filteredAndSortedDatasets = useMemo(() => {
    let sortableItems = [...datasets];

    if (searchTerm) {
      sortableItems = sortableItems.filter(item =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (sortConfig.key) {
      sortableItems.sort((a, b) => {
        const aValue = a[sortConfig.key!];
        const bValue = b[sortConfig.key!];

        if (aValue === null) return 1;
        if (bValue === null) return -1;
        if (aValue < bValue) {
          return sortConfig.direction === 'ascending' ? -1 : 1;
        }
        if (aValue > bValue) {
          return sortConfig.direction === 'ascending' ? 1 : -1;
        }
        return 0;
      });
    }

    return sortableItems;
  }, [datasets, searchTerm, sortConfig]);

  const requestSort = (key: keyof Dataset) => {
    let direction: 'ascending' | 'descending' = 'ascending';
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending';
    }
    setSortConfig({ key, direction });
  };

  const handleRowClick = (datasetId: string) => {
    router.push(`/experiments/${datasetId}`);
  };

  const getSortIndicator = (key: keyof Dataset) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'ascending' ? ' ▲' : ' ▼';
  };

  const handleDownload = () => {
    exportToCsv('datasets.csv', filteredAndSortedDatasets);
  };

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <div className={styles.cardHeader}>
          <div className={styles.headerLeft}>
            <h5 className={styles.cardTitle}>Datasets Disponíveis ({filteredAndSortedDatasets.length})</h5>
            <div className={styles.search_container}>
              <i className="bi bi-search"></i>
              <input
                type="text"
                className="form-control"
                placeholder="Filtrar por nome do dataset..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          <button className={styles.actionButton} title="Download CSV" onClick={handleDownload}>
            <i className="bi bi-download"></i>
          </button>
        </div>
        <div className={`card-body p-0 ${styles.table_responsive}`}>
          <table className={`table table-hover ${styles.table}`}>
            <thead className="table-light">
              <tr>
                <th onClick={() => requestSort('name')} className={`${styles.sortable_header} ${styles.textAlignLeft}`}>
                  Nome {getSortIndicator('name')}
                </th>
                <th scope="col" className={`${styles.sortable_header} ${styles.textAlignLeft}`} onClick={() => requestSort('description')}>
                  Descrição {getSortIndicator('description')}
                </th>
                <th scope="col" className={`${styles.sortable_header} ${styles.textAlignCenter}`} onClick={() => requestSort('exampleCount')}>
                  Exemplos {getSortIndicator('exampleCount')}
                </th>
                <th scope="col" className={`${styles.sortable_header} ${styles.textAlignCenter}`} onClick={() => requestSort('experimentCount')}>
                  Experimentos {getSortIndicator('experimentCount')}
                </th>
                <th scope="col" className={`${styles.sortable_header} ${styles.textAlignCenter}`} onClick={() => requestSort('createdAt')}>
                  Criado em {getSortIndicator('createdAt')}
                </th>
              </tr>
            </thead>
            <tbody>
              {filteredAndSortedDatasets.map((dataset) => (
                <tr key={dataset.id} onClick={() => handleRowClick(dataset.id)}>
                  <td className={styles.textAlignLeft}>{dataset.name}</td>
                  <td className={styles.textAlignLeft}>{dataset.description || 'Sem descrição'}</td>
                  <td className={styles.textAlignCenter}>
                    <span className="badge bg-primary rounded-pill">
                      {dataset.exampleCount}
                    </span>
                  </td>
                  <td className={styles.textAlignCenter}>
                    <span className="badge bg-success rounded-pill">
                      {dataset.experimentCount}
                    </span>
                  </td>
                  <td className={styles.textAlignCenter}>{new Date(dataset.createdAt).toLocaleString('pt-BR')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
