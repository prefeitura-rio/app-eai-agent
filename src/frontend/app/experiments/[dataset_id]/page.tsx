'use client';

import React, { useEffect, useState } from 'react';
import DatasetExperimentsClient from '@/app/experiments/components/dataset-experiments-client';
import { notFound } from 'next/navigation';
import { API_BASE_URL } from '@/app/lib/config';
import { useAuth } from '@/app/contexts/AuthContext';

interface PageProps {
  params: {
    dataset_id: string;
  };
}

export default function DatasetExperimentsPage({ params }: PageProps) {
  const [experimentsData, setExperimentsData] = useState(null);
  const [examplesData, setExamplesData] = useState(null);
  const { token } = useAuth();
  const { dataset_id } = params;

  useEffect(() => {
    if (token) {
      const getDatasetExperiments = async (datasetId: string) => {
        const res = await fetch(`${API_BASE_URL}/api/v1/dataset_experiments?dataset_id=${datasetId}`, {
          headers: { 'Authorization': `Bearer ${token}` },
          cache: 'no-store'
        });
        if (!res.ok) {
          if (res.status === 404) notFound();
          throw new Error('Failed to fetch dataset experiments');
        }
        const data = await res.json();
        setExperimentsData(data.data.dataset);
      };

      const getDatasetExamples = async (datasetId: string) => {
        const res = await fetch(`${API_BASE_URL}/api/v1/dataset_examples?dataset_id=${datasetId}`, {
          headers: { 'Authorization': `Bearer ${token}` },
          cache: 'no-store'
        });
        if (!res.ok) {
          console.error('Failed to fetch dataset examples');
          return;
        }
        const data = await res.json();
        setExamplesData(data.data.dataset.examples.edges.map((edge: any) => edge.example));
      };

      getDatasetExperiments(dataset_id);
      getDatasetExamples(dataset_id);
    }
  }, [token, dataset_id]);

  if (!experimentsData) {
    return <div>Loading...</div>;
  }

  const experiments = experimentsData.experiments.edges.map((edge: any) => edge.experiment);

  return (
    <DatasetExperimentsClient
      experiments={experiments}
      examples={examplesData || []}
      datasetId={dataset_id}
    />
  );
}