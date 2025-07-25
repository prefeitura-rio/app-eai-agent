
'use client';

import React, { useEffect, useState } from 'react';
import ExperimentDetailsClient from '@/app/experiments/components/experiment-details-client';
import { notFound } from 'next/navigation';
import { API_BASE_URL } from '@/app/components/config';
import { useAuth } from '@/app/contexts/AuthContext';

interface PageProps {
  params: Promise<{
    dataset_id: string;
    experiment_id: string;
  }>;
}

export default async function ExperimentDetailsPage({ params }: PageProps) {
  // Await params first
  const { dataset_id, experiment_id } = await params;
  const [data, setData] = useState(null);
  const { token } = useAuth();

  useEffect(() => {
    if (token) {
      const getExperimentData = async (datasetId: string, experimentId: string) => {
        const res = await fetch(`${API_BASE_URL}/api/v1/experiment_data?dataset_id=${datasetId}&experiment_id=${experimentId}`, {
          headers: { 'Authorization': `Bearer ${token}` },
          cache: 'no-store'
        });
        if (!res.ok) {
          if (res.status === 404) notFound();
          throw new Error('Failed to fetch experiment data');
        }
        const jsonData = await res.json();
        setData(jsonData);
      };
      getExperimentData(dataset_id, experiment_id);
    }
  }, [token, dataset_id, experiment_id]);

  if (!data) {
    return <div>Loading...</div>;
  }

  return (
    <ExperimentDetailsClient
      initialData={data}
      datasetId={dataset_id}
      experimentId={experiment_id}
    />
  );
}