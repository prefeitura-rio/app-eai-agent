'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useAuth } from '@/app/contexts/AuthContext';
import AppHeader from '@/app/components/AppHeader';

export default function ExperimentsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = useAuth();
  const pathParts = pathname.split('/').filter(p => p);

  const isRootExperimentsPage = pathname === '/experiments';
  const isDatasetPage = pathParts.length === 2 && pathParts[0] === 'experiments';
  const isExperimentRunPage = pathParts.length === 3 && pathParts[0] === 'experiments';

  const [theme, setTheme] = useState('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-bs-theme', newTheme);
  };

  const handleLogout = () => {
    logout();
    router.push(`/login?redirect_url=${pathname}`);
  };

  const getHeaderActions = () => {
    const baseActions = [
      { id: 'refresh', label: 'Atualizar', icon: 'bi-arrow-clockwise', onClick: () => window.location.reload() },
      { id: 'theme', label: 'Mudar tema', icon: theme === 'light' ? 'bi-moon-fill' : 'bi-sun-fill', onClick: toggleTheme },
      { id: 'logout', label: 'Sair', icon: 'bi-box-arrow-right', onClick: handleLogout, variant: 'logout' as const },
    ];

    if (isRootExperimentsPage) {
      return [{ id: 'home', label: 'Voltar para Home', icon: 'bi-house-door', href: '/' }, ...baseActions];
    }
    
    const backLink = isExperimentRunPage ? `/experiments/${pathParts[1]}` : '/experiments';
    return [{ id: 'back', label: 'Voltar', icon: 'bi-arrow-left', href: backLink }, ...baseActions];
  };

  const getTitle = () => isRootExperimentsPage ? 'Painel de Datasets' : 'Painel de Experimentos';
  const getSubtitle = () => (isDatasetPage || isExperimentRunPage) ? `Dataset: ${pathParts[1]}` : undefined;

  return (
    <div>
      <AppHeader
        title={getTitle()}
        subtitle={getSubtitle()}
        actions={getHeaderActions()}
      />
      <main className="container-xl">
        {children}
      </main>
    </div>
  );
}
