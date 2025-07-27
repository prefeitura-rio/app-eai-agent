'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useEffect, ReactNode } from 'react';
import { useAuth } from '@/app/contexts/AuthContext';
import { HeaderProvider, useHeader } from '@/app/contexts/HeaderContext';
import AppHeader, { ActionButton } from '@/app/components/AppHeader';
import { RefreshCw, LogOut, Home, ArrowLeft } from 'lucide-react';

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
      { id: 'refresh', label: 'Atualizar', icon: RefreshCw, onClick: () => window.location.reload() },
      { id: 'logout', label: 'Sair', icon: LogOut, onClick: handleLogout, variant: 'destructive' },
    ];

    if (isRootExperimentsPage) {
      return [{ id: 'home', label: 'Voltar para Home', icon: Home, href: '/' }, ...pageActions, ...baseActions];
    }
    
    const backLink = pathParts.length === 3 ? `/experiments/${pathParts[1]}` : '/experiments';
    return [...pageActions, { id: 'back', label: 'Voltar', icon: ArrowLeft, href: backLink }, ...baseActions];
  };
  
  return (
    <div className="flex h-screen flex-col">
      <AppHeader
        title={title}
        subtitle={subtitle}
        actions={getHeaderActions()}
      />
      <main className="flex-grow overflow-y-auto">
        {children}
      </main>
    </div>
  );
}

export default function ExperimentsLayout({
  children,
}: {
  children: React.Node;
}) {
  return (
    <HeaderProvider>
      <LayoutContent>{children}</LayoutContent>
    </HeaderProvider>
  );
}
