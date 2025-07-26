'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/app/contexts/AuthContext';
import AppHeader, { ActionButton } from '@/app/components/AppHeader';
import styles from './page.module.css';

export default function HomePage() {
  const { token, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [theme, setTheme] = useState('light');

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-bs-theme', savedTheme);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-bs-theme', newTheme);
  };

  const handleLogout = () => {
    logout();
    router.push(`/login?redirect_url=${pathname}`);
  };

  const headerActions: ActionButton[] = [
    { id: 'theme', label: 'Mudar tema', icon: theme === 'light' ? 'bi-moon-fill' : 'bi-sun-fill', onClick: toggleTheme },
  ];

  if (token) {
    headerActions.push({ id: 'logout', label: 'Sair', icon: 'bi-box-arrow-right', onClick: handleLogout, variant: 'logout' as const });
  }

  return (
    <div className={styles.page_container}>
      <AppHeader title="Painel Administrativo EAI" actions={headerActions} centerTitle={true} />

      <main className={styles.main_content}>
        <p className={styles.description}>
          Navegue pelas seções para gerenciar datasets, analisar experimentos e visualizar resultados.
        </p>
        
        <nav className={styles.nav_grid}>
          <div className={`${styles.nav_card} text-muted`} style={{ cursor: 'not-allowed', filter: 'grayscale(80%)' }}>
             <div className={styles.nav_icon} style={{ backgroundColor: 'var(--color-border)'}}>
              <i className="bi bi-robot" style={{ color: 'var(--color-text-muted)'}}></i>
            </div>
            <div>
              <h3>Configurações EAI</h3>
              <p>Em breve: gerencie system prompts, tools, etc.</p>
            </div>
          </div>
          <Link href="/experiments" className={styles.nav_card}>
            <div className={styles.nav_icon}>
              <i className="bi bi-flask"></i>
            </div>
            <div>
              <h3>Painel de Experimentos</h3>
              <p>Analise e compare os resultados dos experimentos.</p>
            </div>
          </Link>
        </nav>
      </main>
    </div>
  );
}
