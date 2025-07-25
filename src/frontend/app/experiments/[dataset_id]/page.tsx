import React from 'react';
import DatasetExperimentsClient from '@/app/experiments/components/dataset-experiments-client';
import { notFound } from 'next/navigation';

interface PageProps {
  params: {
    dataset_id: string;
  };
}

async function getDatasetExperiments(datasetId: string) {
  const res = await fetch(`http://localhost:3000/api/v1/dataset_experiments?dataset_id=${datasetId}`, { cache: 'no-store' });
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
    const res = await fetch(`http://localhost:3000/api/v1/dataset_examples?dataset_id=${datasetId}`, { cache: 'no-store' });
    if (!res.ok) {
        // It's okay if examples fail, we can still render the page
        console.error('Failed to fetch dataset examples');
        return null;
    }
    const data = await res.json();
    return data.data.dataset.examples.edges.map((edge: any) => edge.example);
}


export default async function DatasetExperimentsPage({ params }: PageProps) {
  const { dataset_id } = params;
  
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
