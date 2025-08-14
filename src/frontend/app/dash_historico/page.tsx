'use client';

import React, { useEffect, useState, Suspense } from 'react';
import DashHistoricoClient from './components/dash-historico-client';
import { API_BASE_URL } from '@/app/components/config';
import { useAuth } from '@/app/contexts/AuthContext';
import DashHistoricoSkeleton from './components/dash-historico-skeleton';

interface WhitelistData {
  [groupName: string]: string[];
}

function DashHistoricoPageContent() {
  const [whitelist, setWhitelist] = useState<WhitelistData>({});
  const [loading, setLoading] = useState(true);
  const { token } = useAuth();

  useEffect(() => {
    if (token) {
      const getWhitelist = async () => {
        setLoading(true);
        try {
          const res = await fetch(`${API_BASE_URL}/api/v1/rmi/whitelist`, {
            headers: { 'Authorization': `Bearer ${token}` },
            cache: 'no-store'
          });

          if (!res.ok) {
            throw new Error('Failed to fetch whitelist');
          }

          const data = await res.json();
          setWhitelist(data);
        } catch (error) {
          console.error(error);
          setWhitelist({});
        } finally {
          setLoading(false);
        }
      };
      getWhitelist();
    }
  }, [token]);

  if (loading) {
    return <DashHistoricoSkeleton />;
  }

  return <DashHistoricoClient whitelist={whitelist} />;
}

export default function DashHistoricoPage() {
    return (
        <Suspense fallback={<DashHistoricoSkeleton />}>
            <DashHistoricoPageContent />
        </Suspense>
    )
}