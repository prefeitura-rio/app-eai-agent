'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState, ReactNode } from 'react';
import { useAuth } from '@/app/contexts/AuthContext';
import { HeaderProvider, useHeader } from '@/app/contexts/HeaderContext';
import AppHeader from '@/app/components/AppHeader';

function LayoutContent({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = useAuth();
  const { title, subtitle, setTitle, setSubtitle, pageActions } = useHeader(); // Get pageActions
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

  useEffect(() => {
    if (isRootExperimentsPage) {
      setTitle('Painel de Datasets');
      setSubtitle('Selecione um dataset para ver os experimentos');
    } else if (isDatasetPage) {
        setTitle('Experimentos do Dataset');
    }
  }, [pathname, isRootExperimentsPage, isDatasetPage, setTitle, setSubtitle]);

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
      return [{ id: 'home', label: 'Voltar para Home', icon: 'bi-house-door', href: '/' }, ...pageActions, ...baseActions];
    }
    
    const backLink = isExperimentRunPage ? `/experiments/${pathParts[1]}` : '/experiments';
    return [...pageActions, { id: 'back', label: 'Voltar', icon: 'bi-arrow-left', href: backLink }, ...baseActions];
  };
  
  return (
    <div style={{ height: '100vh', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
      <AppHeader
        title={title}
        subtitle={subtitle}
        actions={getHeaderActions()}
      />
      <main style={{ flexGrow: 1, overflow: 'hidden' }}>
        {children}
      </main>
    </div>
  );
}

export default function ExperimentsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <HeaderProvider>
      <LayoutContent>{children}</LayoutContent>
    </HeaderProvider>
  );
}