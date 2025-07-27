'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/app/contexts/AuthContext';
import AppHeader, { ActionButton } from '@/app/components/AppHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

export default function HomePage() {
  const { token, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    logout();
    router.push(`/login?redirect_url=${pathname}`);
  };

  const headerActions: ActionButton[] = [];

  if (token) {
    headerActions.push({ id: 'logout', label: 'Sair', icon: 'bi-box-arrow-right', onClick: handleLogout, variant: 'destructive' });
  }

  return (
    <div className="flex min-h-screen flex-col">
      <AppHeader title="Painel Administrativo EAI" actions={headerActions} centerTitle={true} />

      <main className="container mx-auto flex-grow text-center flex flex-col items-center justify-center px-4">
        <p className="mx-auto max-w-2xl text-lg text-muted-foreground mb-12">
          Navegue pelas seções para gerenciar datasets, analisar experimentos e visualizar resultados.
        </p>
        
        <nav className="mx-auto grid w-full max-w-4xl gap-8 sm:grid-cols-2">
          <Card className="text-left bg-card/50 grayscale cursor-not-allowed">
            <CardHeader className="flex-row items-center gap-4">
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                <i className="bi bi-robot text-2xl text-muted-foreground"></i>
              </div>
              <div>
                <CardTitle className="text-lg text-muted-foreground">Configurações EAI</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">Em breve: gerencie system prompts, tools, etc.</p>
            </CardContent>
          </Card>
          
          <Link href="/experiments" className="group">
            <Card className="text-left transition-all group-hover:-translate-y-1 group-hover:shadow-lg group-hover:border-primary/50">
              <CardHeader className="flex-row items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary/20">
                  <i className="bi bi-flask text-2xl"></i>
                </div>
                <div>
                  <CardTitle className="text-lg">Painel de Experimentos</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">Analise e compare os resultados dos experimentos.</p>
              </CardContent>
            </Card>
          </Link>
        </nav>
      </main>
    </div>
  );
}
