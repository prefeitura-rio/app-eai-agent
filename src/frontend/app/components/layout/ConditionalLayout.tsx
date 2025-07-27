'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import { SidebarProvider } from '@/app/contexts/SidebarContext';
import { Sidebar } from '@/app/components/layout/sidebar';

export default function ConditionalLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLoginPage = pathname === '/login';

  if (isLoginPage) {
    return <>{children}</>;
  }

  return (
    <SidebarProvider>
      <div className="flex h-screen w-full bg-background">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-y-auto">
          {children}
        </div>
      </div>
    </SidebarProvider>
  );
}