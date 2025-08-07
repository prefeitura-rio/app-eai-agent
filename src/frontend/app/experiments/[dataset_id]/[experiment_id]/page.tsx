'use client';

import React, { useEffect, useState, Suspense, use } from 'react';
import { notFound } from 'next/navigation';
import { API_BASE_URL } from '@/app/components/config';
import { useAuth } from '@/app/contexts/AuthContext';
import { ExperimentDetails } from '../../types';
import ExperimentDetailsClient from './components/experiment-details-client';
import ExperimentDetailsSkeleton from './components/experiment-details-skeleton';

interface PageProps {
  params: Promise<{
    dataset_id: string;
    experiment_id: string;
  }>;
}

function ExperimentDetailsPageContent({ datasetId, experimentId }: { datasetId: string, experimentId: string }) {
    const [experimentData, setExperimentData] = useState<ExperimentDetails | null>(null);
    const [loading, setLoading] = useState(true);
    const { token } = useAuth();

    useEffect(() => {
        if (token) {
            const getExperimentData = async () => {
                setLoading(true);
                try {
                    const res = await fetch(`${API_BASE_URL}/api/v1/experiments?dataset_id=${datasetId}&experiment_id=${experimentId}`, {
                        headers: { 'Authorization': `Bearer ${token}` },
                        cache: 'no-store'
                    });

                    if (!res.ok) {
                        if (res.status === 404) notFound();
                        throw new Error('Failed to fetch experiment details');
                    }

                    const data = await res.json();
                    console.log('Dados recebidos da API:', data);
                    setExperimentData(data);

                } catch (error) {
                    console.error(error);
                } finally {
                    setLoading(false);
                }
            };
            getExperimentData();
        }
    }, [token, datasetId, experimentId]);

    if (loading || !experimentData) {
        return <ExperimentDetailsSkeleton />;
    }

    return <ExperimentDetailsClient experimentData={experimentData} />;
}


export default function ExperimentDetailsPage({ params }: PageProps) {
    const { dataset_id, experiment_id } = use(params);

    return (
        <div className="h-screen overflow-hidden">
            <Suspense fallback={<ExperimentDetailsSkeleton />}>
                <ExperimentDetailsPageContent datasetId={dataset_id} experimentId={experiment_id} />
            </Suspense>
        </div>
    );
}
