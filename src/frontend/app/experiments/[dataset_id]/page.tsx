'use client';

import React, { useEffect, useState, Suspense, use } from 'react';
import { notFound } from 'next/navigation';
import { API_BASE_URL } from '@/app/components/config';
import { useAuth } from '@/app/contexts/AuthContext';
import { DatasetExperimentInfo, DatasetExamplesInfo } from '../types';
import DatasetDetailsClient from './components/dataset-details-client';
import DatasetDetailsSkeleton from './components/dataset-details-skeleton';

interface PageProps {
  params: Promise<{
    dataset_id: string;
  }>;
}

function DatasetDetailsPageContent({ datasetId }: { datasetId: string }) {
    const [experiments, setExperiments] = useState<DatasetExperimentInfo[] | null>(null);
    const [examples, setExamples] = useState<DatasetExamplesInfo[] | null>(null);
    const [loading, setLoading] = useState(true);
    const { token } = useAuth();

    useEffect(() => {
        if (token) {
            const getDatasetData = async (id: string) => {
                setLoading(true);
                try {
                    const [expRes, exRes] = await Promise.all([
                        fetch(`${API_BASE_URL}/api/v1/dataset_experiments?dataset_id=${id}`, {
                            headers: { 'Authorization': `Bearer ${token}` },
                            cache: 'no-store'
                        }),
                        fetch(`${API_BASE_URL}/api/v1/dataset_examples?dataset_id=${id}`, {
                            headers: { 'Authorization': `Bearer ${token}` },
                            cache: 'no-store'
                        })
                    ]);

                    if (!expRes.ok || !exRes.ok) {
                        if (expRes.status === 404 || exRes.status === 404) notFound();
                        throw new Error('Failed to fetch dataset details');
                    }

                    const expData = await expRes.json();
                    const exData = await exRes.json();
                    
                    setExperiments(expData);
                    setExamples(exData);

                } catch (error) {
                    console.error(error);
                } finally {
                    setLoading(false);
                }
            };
            getDatasetData(datasetId);
        }
    }, [token, datasetId]);

    if (loading || !experiments || !examples) {
        return <DatasetDetailsSkeleton />;
    }

    return (
        <DatasetDetailsClient
            experiments={experiments}
            examples={examples[0]?.examples || []}
            datasetId={datasetId}
        />
    );
}


export default function DatasetDetailsPage({ params }: PageProps) {
    const { dataset_id } = use(params);

    return (
        <Suspense fallback={<DatasetDetailsSkeleton />}>
            <DatasetDetailsPageContent datasetId={dataset_id} />
        </Suspense>
    );
}
