'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import Cookies from 'js-cookie';

interface AuthContextType {
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const tokenFromCookie = Cookies.get('auth_token');
    if (tokenFromCookie) {
      setToken(tokenFromCookie);
    }
  }, []);

  const login = (newToken: string) => {
    setToken(newToken);
    Cookies.set('auth_token', newToken, { expires: 7, secure: true, sameSite: 'strict' });
  };

  const logout = () => {
    setToken(null);
    Cookies.remove('auth_token');
  };

  return (
    <AuthContext.Provider value={{ token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
