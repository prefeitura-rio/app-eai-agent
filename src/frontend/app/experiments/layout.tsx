'use client';

import { usePathname } from 'next/navigation';
import { useEffect, ReactNode } from 'react';
import { HeaderProvider, useHeader } from '@/app/contexts/HeaderContext';
import AppHeader, { ActionButton } from '@/app/components/AppHeader';
import { RefreshCw } from 'lucide-react';

function LayoutContent({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { title, subtitle, setTitle, setSubtitle, pageActions } = useHeader();
  const pathParts = pathname.split('/').filter(p => p);

  const isRootExperimentsPage = pathname === '/experiments';
  const isDatasetPage = pathParts.length === 2 && pathParts[0] === 'experiments';
  const isExperimentDetailsPage = pathParts.length === 3 && pathParts[0] === 'experiments';

  useEffect(() => {
    if (isRootExperimentsPage) {
      setTitle('Painel de Datasets');
      setSubtitle('Selecione um dataset para ver os experimentos');
    } else if (isDatasetPage) {
        setTitle('Experimentos do Dataset');
    } else if (isExperimentDetailsPage) {
        setTitle('Detalhes do Experimento');
    }
  }, [pathname, isRootExperimentsPage, isDatasetPage, isExperimentDetailsPage, setTitle, setSubtitle]);

  const getHeaderActions = (): ActionButton[] => {
    const actions: ActionButton[] = [...pageActions];
    // Refresh button has been moved to the client components
    return actions;
  };
  
  return (
    <div className="flex flex-col h-full">
      <AppHeader
        title={title}
        subtitle={subtitle}
        actions={getHeaderActions()}
      />
      <main className="flex-1 overflow-hidden">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 h-full">
          {children}
        </div>
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
