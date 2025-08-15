'use client';

import { ReactNode } from 'react';
import { HeaderProvider } from '@/app/contexts/HeaderContext';
import AppHeader from '@/app/components/AppHeader';
import { useHeader } from '@/app/contexts/HeaderContext';

function LayoutContent({ children }: { children: ReactNode }) {
  const { title, subtitle, pageActions } = useHeader();

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      <AppHeader
        title={title || 'Carregando...'}
        subtitle={subtitle}
        actions={pageActions}
      />
      <main className="flex-1 overflow-hidden">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 h-full">
          {children}
        </div>
      </main>
    </div>
  );
}

export default function DashHistoricoLayout({
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