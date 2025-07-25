'use client';

import React, { useState, useMemo, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Dataset } from '@/app/components/types';

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

    // Filter
    if (searchTerm) {
      sortableItems = sortableItems.filter(item =>
        item.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Sort
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
  
  // ... rest of the component is the same

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

  return (
    <div className="">
      <div className="">
        <h2 className="">Datasets Disponíveis ({filteredAndSortedDatasets.length})</h2>
        <input
          type="text"
          placeholder="Filtrar por nome..."
          className=""
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      <div className="">
        <table className="">
          <thead className="">
            <tr>
              <th scope="col" className="" onClick={() => requestSort('name')}>
                Nome {getSortIndicator('name')}
              </th>
              <th scope="col" className="" onClick={() => requestSort('description')}>
                Descrição {getSortIndicator('description')}
              </th>
              <th scope="col" className="" onClick={() => requestSort('exampleCount')}>
                Exemplos {getSortIndicator('exampleCount')}
              </th>
              <th scope="col" className="" onClick={() => requestSort('experimentCount')}>
                Experimentos {getSortIndicator('experimentCount')}
              </th>
              <th scope="col" className="" onClick={() => requestSort('createdAt')}>
                Criado em {getSortIndicator('createdAt')}
              </th>
            </tr>
          </thead>
          <tbody className="">
            {filteredAndSortedDatasets.map((dataset) => (
              <tr key={dataset.id} onClick={() => handleRowClick(dataset.id)} className="">
                <td className="">{dataset.name}</td>
                <td className="">{dataset.description || 'Sem descrição'}</td>
                <td className="">
                  <span className="">
                    {dataset.exampleCount}
                  </span>
                </td>
                <td className="">
                  <span className="">
                    {dataset.experimentCount}
                  </span>
                </td>
                <td className="">{new Date(dataset.createdAt).toLocaleString('pt-BR')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}