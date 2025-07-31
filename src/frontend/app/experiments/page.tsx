'use client';

import React, { useEffect, useState, Suspense } from 'react';
import DatasetsClient from './components/datasets-client';
import { API_BASE_URL } from '@/app/components/config';
import { useAuth } from '@/app/contexts/AuthContext';
import { DatasetInfo } from './types';
import DatasetsSkeleton from './components/datasets-skeleton';

function DatasetsPageContent() {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const { token } = useAuth();

  useEffect(() => {
    if (token) {
      const getDatasets = async () => {
        setLoading(true);
        try {
          const res = await fetch(`${API_BASE_URL}/api/v1/datasets`, {
            headers: { 'Authorization': `Bearer ${token}` },
            cache: 'no-store'
          });

          if (!res.ok) {
            throw new Error('Failed to fetch datasets');
          }

          const data = await res.json();
          setDatasets(data);
        } catch (error) {
          console.error(error);
          setDatasets([]);
        } finally {
          setLoading(false);
        }
      };
      getDatasets();
    }
  }, [token]);

  if (loading) {
    return <DatasetsSkeleton />;
  }

  return <DatasetsClient datasets={datasets} />;
}

export default function DatasetsPage() {
    return (
        <Suspense fallback={<DatasetsSkeleton />}>
            <DatasetsPageContent />
        </Suspense>
    )
}
