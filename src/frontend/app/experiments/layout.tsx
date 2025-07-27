'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useEffect, ReactNode } from 'react';
import { useAuth } from '@/app/contexts/AuthContext';
import { HeaderProvider, useHeader } from '@/app/contexts/HeaderContext';
import AppHeader, { ActionButton } from '@/app/components/AppHeader';

function LayoutContent({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { logout } = useAuth();
  const { title, subtitle, setTitle, setSubtitle, pageActions } = useHeader();
  const pathParts = pathname.split('/').filter(p => p);

  const isRootExperimentsPage = pathname === '/experiments';
  const isDatasetPage = pathParts.length === 2 && pathParts[0] === 'experiments';

  useEffect(() => {
    if (isRootExperimentsPage) {
      setTitle('Painel de Datasets');
      setSubtitle('Selecione um dataset para ver os experimentos');
    } else if (isDatasetPage) {
        setTitle('Experimentos do Dataset');
    }
  }, [pathname, isRootExperimentsPage, isDatasetPage, setTitle, setSubtitle]);

  const handleLogout = () => {
    logout();
    router.push(`/login?redirect_url=${pathname}`);
  };

  const getHeaderActions = (): ActionButton[] => {
    const baseActions: ActionButton[] = [
      { id: 'refresh', label: 'Atualizar', icon: 'bi-arrow-clockwise', onClick: () => window.location.reload() },
      { id: 'logout', label: 'Sair', icon: 'bi-box-arrow-right', onClick: handleLogout, variant: 'destructive' },
    ];

    if (isRootExperimentsPage) {
      return [{ id: 'home', label: 'Voltar para Home', icon: 'bi-house-door', href: '/' }, ...pageActions, ...baseActions];
    }
    
    const backLink = pathParts.length === 3 ? `/experiments/${pathParts[1]}` : '/experiments';
    return [...pageActions, { id: 'back', label: 'Voltar', icon: 'bi-arrow-left', href: backLink }, ...baseActions];
  };
  
  return (
    <div className="flex h-screen flex-col">
      <AppHeader
        title={title}
        subtitle={subtitle}
        actions={getHeaderActions()}
      />
      <main className="flex-grow overflow-hidden">
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