import React from 'react';
import DatasetsClient from '@/app/experiments/components/datasets-client';

async function getDatasets() {
  // The fetch URL is relative because of the rewrite rule in next.config.ts
  const res = await fetch('http://localhost:3000/api/v1/datasets', { cache: 'no-store' });

  if (!res.ok) {
    // This will activate the closest `error.js` Error Boundary
    throw new Error('Failed to fetch data');
  }

  const data = await res.json();
  // The API returns data in a nested structure
  return data.data.datasets.edges.map((edge: any) => edge.node);
}

export default async function DatasetsPage() {
  const datasets = await getDatasets();

  return (
    <DatasetsClient datasets={datasets} />
  );
}
