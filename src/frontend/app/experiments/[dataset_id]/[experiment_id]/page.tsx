
'use client';

import React, { useEffect, useState, use } from 'react';
import ExperimentDetailsClient from './components/experiment-details-client';
import { notFound } from 'next/navigation';
import { API_BASE_URL } from '@/app/components/config';
import { useAuth } from '@/app/contexts/AuthContext';
import { ExperimentData } from '@/app/components/types';
import { LlmJsonFilters } from './components/DownloadLlmJsonModal';
import { downloadFile } from '@/app/utils/csv';

import ExperimentDetailsSkeleton from './components/ExperimentDetailsSkeleton';

interface PageProps {
  params: Promise<{
    dataset_id: string;
    experiment_id: string;
  }>;
}

export default function ExperimentDetailsPage({ params }: PageProps) {
  const { dataset_id, experiment_id } = use(params);
  const [data, setData] = useState<ExperimentData | null>(null);
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

  const handleDownloadCleanJson = async (numExperiments: number | null, filters: LlmJsonFilters): Promise<boolean> => {
    if (!token) {
        console.error("Authentication token not found.");
        return false;
    }

    const params = new URLSearchParams();
    if (numExperiments) {
        params.append('number_of_random_experiments', String(numExperiments));
    }
    params.append('filters', JSON.stringify(filters));

    try {
        const res = await fetch(`${API_BASE_URL}/api/v1/experiment_data_clean?dataset_id=${dataset_id}&experiment_id=${experiment_id}&${params.toString()}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.ok) {
            const blob = await res.blob();
            const experiment_name = data?.experiment_name || "experiment";
            downloadFile(`experiment_${experiment_name}_clean.json`, blob);
            return true;
        } else {
            console.error("Failed to download clean JSON", res.status, await res.text());
            return false;
        }
    } catch (error) {
        console.error("Error during fetch for clean JSON download:", error);
        return false;
    }
  };

  if (!data) {
    return <ExperimentDetailsSkeleton />;
  }

  return (
    <ExperimentDetailsClient
      initialData={data}
      datasetId={dataset_id}
      experimentId={experiment_id}
      handleDownloadCleanJson={handleDownloadCleanJson}
    />
  );
}