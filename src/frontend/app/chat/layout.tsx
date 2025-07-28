'use client';

import { ReactNode } from 'react';
import { HeaderProvider } from '@/app/contexts/HeaderContext';
import AppHeader from '@/app/components/AppHeader';

function LayoutContent({ children }: { children: ReactNode }) {
  return (
    <div className="flex flex-col h-screen">
      <AppHeader
        title="Chat EAI"
        subtitle="Converse diretamente com o modelo do letta"
      />
      <main className="flex-1 overflow-hidden">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 h-full py-6">
          {children}
        </div>
      </main>
    </div>
  );
}

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  return (
    <HeaderProvider>
      <LayoutContent>{children}</LayoutContent>
    </HeaderProvider>
  );
}