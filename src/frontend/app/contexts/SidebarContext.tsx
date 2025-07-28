'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

type SidebarState = 'expanded' | 'collapsed';

interface SidebarContextType {
  state: SidebarState;
  setState: (state: SidebarState) => void;
  toggle: () => void;
}

const SidebarContext = createContext<SidebarContextType | undefined>(undefined);

export const SidebarProvider = ({ children }: { children: ReactNode }) => {
  const [state, setState] = useState<SidebarState>('expanded');

  const toggle = () => {
    setState(prevState => prevState === 'expanded' ? 'collapsed' : 'expanded');
  };

  return (
    <SidebarContext.Provider value={{ state, setState, toggle }}>
      {children}
    </SidebarContext.Provider>
  );
};

export const useSidebar = () => {
  const context = useContext(SidebarContext);
  if (context === undefined) {
    throw new Error('useSidebar must be used within a SidebarProvider');
  }
  return context;
};
