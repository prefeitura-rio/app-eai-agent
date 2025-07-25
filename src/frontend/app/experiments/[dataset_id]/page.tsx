import React from 'react';
import DatasetExperimentsClient from '@/app/experiments/components/dataset-experiments-client';
import { notFound } from 'next/navigation';
import { API_BASE_URL } from '@/app/lib/config';

interface PageProps {
  params: Promise<{
    dataset_id: string;
  }>;
}

export default async function DatasetExperimentsPage({ params }: PageProps) {
  // Await params first
  const { dataset_id } = await params;

  async function getDatasetExperiments(datasetId: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/dataset_experiments?dataset_id=${datasetId}`, { cache: 'no-store' });
    if (!res.ok) {
      if (res.status === 404) {
        notFound();
      }
      throw new Error('Failed to fetch dataset experiments');
    }
    const data = await res.json();
    return data.data.dataset;
  }

  async function getDatasetExamples(datasetId: string) {
      const res = await fetch(`${API_BASE_URL}/api/v1/dataset_examples?dataset_id=${datasetId}`, { cache: 'no-store' });
      if (!res.ok) {
          console.error('Failed to fetch dataset examples');
          return null;
      }
      const data = await res.json();
      return data.data.dataset.examples.edges.map((edge: any) => edge.example);
  }

  // Fetch data in parallel
  const [experimentsData, examplesData] = await Promise.all([
    getDatasetExperiments(dataset_id),
    getDatasetExamples(dataset_id)
  ]);

  if (!experimentsData) {
    notFound();
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