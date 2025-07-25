
import React from 'react';
import ExperimentDetailsClient from '@/app/experiments/components/experiment-details-client';
import { notFound } from 'next/navigation';
import { API_BASE_URL } from '@/app/lib/config';

interface PageProps {
  params: Promise<{
    dataset_id: string;
    experiment_id: string;
  }>;
}

export default async function ExperimentDetailsPage({ params }: PageProps) {
  // Await params first
  const { dataset_id, experiment_id } = await params;

  async function getExperimentData(datasetId: string, experimentId: string) {
    const res = await fetch(`${API_BASE_URL}/api/v1/experiment_data?dataset_id=${datasetId}&experiment_id=${experimentId}`, { cache: 'no-store' });
    if (!res.ok) {
      if (res.status === 404) {
        notFound();
      }
      throw new Error('Failed to fetch experiment data');
    }
    return res.json();
  }

  const data = await getExperimentData(dataset_id, experiment_id);

  if (!data) {
    notFound();
  }

  return (
    <ExperimentDetailsClient
      initialData={data}
      datasetId={dataset_id}
      experimentId={experiment_id}
    />
  );
}