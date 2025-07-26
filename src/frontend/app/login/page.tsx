'use client';

import { useState, Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/app/contexts/AuthContext';
import { API_BASE_URL } from '@/app/components/config';
import styles from './page.module.css';

function LoginForm() {
  const [token, setToken] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    document.body.classList.add(styles.auth_page);
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
    
    return () => {
      document.body.classList.remove(styles.auth_page);
    };
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-bs-theme', newTheme);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    if (!token.trim()) {
      setError('O token não pode estar vazio.');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth?token=${token}`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error('Token inválido');
      }

      login(token);
      const redirectUrl = searchParams.get('redirect_url');
      router.push(redirectUrl || '/');
    } catch (_err) {
      setError('Token inválido. Por favor, tente novamente.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.auth_container}>
      <div className={styles.theme_toggle}>
        <button onClick={toggleTheme} className={styles.theme_btn} title={`Mudar para tema ${theme === 'light' ? 'escuro' : 'claro'}`}>
          <i className={`bi ${theme === 'light' ? 'bi-moon-fill' : 'bi-sun-fill'}`}></i>
        </button>
      </div>
      
      <div className={styles.auth_header}>
        <h1>Autenticação</h1>
        <p>Por favor, insira seu Bearer Token para continuar.</p>
      </div>
      
      <form onSubmit={handleSubmit}>
        <div className={styles.form_group}>
          <label htmlFor="token-input" className={styles.form_label}>Bearer Token</label>
          <textarea
            id="token-input"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className={styles.form_control}
            required
            placeholder="Cole seu token aqui..."
            rows={5}
          />
        </div>
        
        {error && <p className={styles.error_message}>{error}</p>}
        
        <button
          type="submit"
          disabled={isLoading}
          className={styles.btn_auth}
        >
          {isLoading ? 'Validando...' : 'Entrar'}
        </button>
      </form>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div>Carregando...</div>}>
      <LoginForm />
    </Suspense>
  );
}