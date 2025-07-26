'use client';

import React, { createContext, useContext, useState, ReactNode } from 'react';

interface HeaderContextType {
  subtitle: string | null;
  setSubtitle: (subtitle: string | null) => void;
}

const HeaderContext = createContext<HeaderContextType | undefined>(undefined);

export const HeaderProvider = ({ children }: { children: ReactNode }) => {
  const [subtitle, setSubtitle] = useState<string | null>(null);

  return (
    <HeaderContext.Provider value={{ subtitle, setSubtitle }}>
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
