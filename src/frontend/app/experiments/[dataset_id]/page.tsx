'use client';

import React, { useEffect, useState, use } from 'react';
import DatasetExperimentsClient from './components/dataset-experiments-client';
import { notFound } from 'next/navigation';
import { API_BASE_URL } from '@/app/components/config';
import { useAuth } from '@/app/contexts/AuthContext';
import { useHeader } from '@/app/contexts/HeaderContext';
import { Experiment, Example } from '@/app/components/types';

interface PageProps {
  params: Promise<{
    dataset_id: string;
  }>;
}

export default function DatasetExperimentsPage({ params }: PageProps) {
  const { dataset_id } = use(params);
  const [experiments, setExperiments] = useState<Experiment[]>([]);
  const [examples, setExamples] = useState<Example[]>([]);
  const [datasetName, setDatasetName] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const { token } = useAuth();
  const { setSubtitle } = useHeader();

  useEffect(() => {
    // Reset subtitle on component mount or when dataset_id changes
    setSubtitle(null);

    if (token) {
      const getDatasetData = async (datasetId: string) => {
        setLoading(true);
        try {
          // Fetch experiments and dataset name together
          const expRes = await fetch(`${API_BASE_URL}/api/v1/dataset_experiments?dataset_id=${datasetId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
            cache: 'no-store'
          });

          if (!expRes.ok) {
            if (expRes.status === 404) notFound();
            throw new Error('Failed to fetch dataset experiments');
          }
          const expData = await expRes.json();
          const dataset = expData.data.dataset;
          
          setExperiments(dataset.experiments.edges.map((edge: { experiment: Experiment }) => edge.experiment));
          setDatasetName(dataset.name);
          setSubtitle(`${dataset.name}`);

          // Fetch examples separately
          const exRes = await fetch(`${API_BASE_URL}/api/v1/dataset_examples?dataset_id=${datasetId}`, {
            headers: { 'Authorization': `Bearer ${token}` },
            cache: 'no-store'
          });

          if (exRes.ok) {
            const exData = await exRes.json();
            setExamples(exData.data.dataset.examples.edges.map((edge: { example: Example }) => edge.example));
          } else {
            console.error('Failed to fetch dataset examples');
          }

        } catch (error) {
          console.error(error);
          setSubtitle('Dataset não encontrado');
        } finally {
          setLoading(false);
        }
      };
      getDatasetData(dataset_id);
    }
  }, [token, dataset_id, setSubtitle]);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <DatasetExperimentsClient
      experiments={experiments}
      examples={examples}
      datasetId={dataset_id}
      datasetName={datasetName}
    />
  );
}
