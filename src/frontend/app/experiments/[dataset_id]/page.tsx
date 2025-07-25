'use client';

import React, { useEffect, useState } from 'react';
import DatasetExperimentsClient from '@/app/experiments/components/dataset-experiments-client';
import { notFound } from 'next/navigation';
import { API_BASE_URL } from '@/app/components/config';
import { useAuth } from '@/app/contexts/AuthContext';
import { Experiment, Example } from '@/app/components/types';

interface PageProps {
  params: Promise<{
    dataset_id: string;
  }>;
}

export default async function DatasetExperimentsPage({ params }: PageProps) {
  // Await params first
  const { dataset_id } = await params;
  const [experimentsData, setExperimentsData] = useState<{ experiments: { edges: Array<{ experiment: Experiment }> }, name: string } | null>(null);
  const [examplesData, setExamplesData] = useState<Example[] | null>(null);
  const { token } = useAuth();

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
        setExamplesData(data.data.dataset.examples.edges.map((edge: { example: Example }) => edge.example));
      };

      getDatasetExperiments(dataset_id);
      getDatasetExamples(dataset_id);
    }
  }, [token, dataset_id]);

  if (!experimentsData) {
    return <div>Loading...</div>;
  }

  const experiments = experimentsData.experiments.edges.map((edge: { experiment: Experiment }) => edge.experiment);

  return (
    <DatasetExperimentsClient
      experiments={experiments}
      examples={examplesData || []}
      datasetId={dataset_id}
    />
  );
}
