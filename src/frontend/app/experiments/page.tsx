import React from 'react';
import DatasetsClient from '@/app/experiments/components/datasets-client';
import { API_BASE_URL } from '@/app/lib/config';

async function getDatasets() {
  const res = await fetch(`${API_BASE_URL}/api/v1/datasets`, { cache: 'no-store' });

  if (!res.ok) {
    throw new Error('Failed to fetch data');
  }

  const data = await res.json();
  return data.data.datasets.edges.map((edge: any) => edge.node);
}

export default async function DatasetsPage() {
  const datasets = await getDatasets();

  return (
    <DatasetsClient datasets={datasets} />
  );
}
