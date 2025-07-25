'use client';

import React, { useEffect, useState } from 'react';
import DatasetsClient from '@/app/experiments/components/datasets-client';
import { API_BASE_URL } from '@/app/lib/config';
import { useAuth } from '@/app/contexts/AuthContext';

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState([]);
  const { token } = useAuth();

  useEffect(() => {
    if (token) {
      const getDatasets = async () => {
        const res = await fetch(`${API_BASE_URL}/api/v1/datasets`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          cache: 'no-store'
        });

        if (!res.ok) {
          throw new Error('Failed to fetch data');
        }

        const data = await res.json();
        setDatasets(data.data.datasets.edges.map((edge: any) => edge.node));
      };
      getDatasets();
    }
  }, [token]);

  return (
    <DatasetsClient datasets={datasets} />
  );
}
