'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { ActionButton } from '@/app/components/AppHeader'; // Import the type

interface HeaderContextType {
  title: string | null;
  setTitle: (title: string | null) => void;
  subtitle: string | null;
  setSubtitle: (subtitle: string | null) => void;
  pageActions: ActionButton[];
  setPageActions: (actions: ActionButton[]) => void;
}

const HeaderContext = createContext<HeaderContextType | undefined>(undefined);

export const HeaderProvider = ({ children }: { children: ReactNode }) => {
  const [title, setTitle] = useState<string | null>('Página de Experimentos');
  const [subtitle, setSubtitle] = useState<string | null>('Selecione um dataset para começar');
  const [pageActions, setPageActions] = useState<ActionButton[]>([]);

  return (
    <HeaderContext.Provider value={{ title, setTitle, subtitle, setSubtitle, pageActions, setPageActions }}>
      {children}
    </HeaderContext.Provider>
  );
};

export const useHeader = () => {
  const context = useContext(HeaderContext);
  if (context === undefined) {
    throw new Error('useHeader must be used within a HeaderProvider');
  }
  return context;
};
