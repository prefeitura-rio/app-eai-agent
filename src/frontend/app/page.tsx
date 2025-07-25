'use client';

import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { useAuth } from '@/app/contexts/AuthContext';

export default function HomePage() {
  const { token, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();

  const handleLogout = () => {
    logout();
    router.push(`/login?redirect_url=${pathname}`);
  };

  return (
    <div className="">
      {token && (
        <div className="">
          <button 
            onClick={handleLogout} 
            className=""
          >
            Sair
          </button>
        </div>
      )}
      <div className="">
        <h1 className="">Bem-vindo!</h1>
        <p className="">
          Selecione uma página para começar.
        </p>
        <nav>
          <ul>
            <li>
              <Link href="/experiments" className="">
                Experiments Datasets
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  );
}
