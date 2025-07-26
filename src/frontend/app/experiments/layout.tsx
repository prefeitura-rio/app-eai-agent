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
  const { title, subtitle, setTitle, setSubtitle } = useHeader();
  const pathParts = pathname.split('/').filter(p => p);

  const isRootExperimentsPage = pathname === '/experiments';
  const isDatasetPage = pathParts.length === 2 && pathParts[0] === 'experiments';
  const isExperimentRunPage = pathParts.length === 4 && pathParts[1] === 'experiments';

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
        // Subtitle for dataset page will be set by the page itself
    }
    // For experiment run page, title and subtitle are set by the page
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
      return [{ id: 'home', label: 'Voltar para Home', icon: 'bi-house-door', href: '/' }, ...baseActions];
    }
    
    const backLink = isExperimentRunPage ? `/experiments/${pathParts[2]}` : '/experiments';
    return [{ id: 'back', label: 'Voltar', icon: 'bi-arrow-left', href: backLink }, ...baseActions];
  };
  
  return (
    <div>
      <AppHeader
        title={title}
        subtitle={subtitle}
        actions={getHeaderActions()}
      />
      <main>
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