'use client';

import { useEffect, ReactNode } from 'react';
import { HeaderProvider, useHeader } from '@/app/contexts/HeaderContext';
import AppHeader from '@/app/components/AppHeader';

function LayoutContent({ children }: { children: ReactNode }) {
  const { title, subtitle, pageActions, setTitle, setSubtitle } = useHeader();

  // O título e as ações serão definidos pelo componente cliente da página
  useEffect(() => {
    setTitle('Configurações EAI');
    setSubtitle('Gerencie os prompts e configurações dos agentes');
  }, [setTitle, setSubtitle]);
  
  return (
    <div className="flex flex-col h-screen">
      <AppHeader
        title={title}
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

export default function EaiSettingsLayout({
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
