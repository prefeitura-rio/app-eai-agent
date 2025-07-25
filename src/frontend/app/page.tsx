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
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 relative">
      {token && (
        <div className="absolute top-4 right-4">
          <button 
            onClick={handleLogout} 
            className="px-3 py-2 border rounded-md border-red-500 text-red-500 hover:bg-red-500 hover:text-white"
          >
            Sair
          </button>
        </div>
      )}
      <div className="max-w-md w-full bg-white dark:bg-gray-800 shadow-md rounded-lg p-8">
        <h1 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-6">Bem-vindo!</h1>
        <p className="text-center text-gray-600 dark:text-gray-400 mb-8">
          Selecione uma página para começar.
        </p>
        <nav>
          <ul>
            <li>
              <Link href="/experiments" className="block w-full text-center bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-4 rounded-lg transition duration-300">
                Experiments Datasets
              </Link>
            </li>
          </ul>
        </nav>
      </div>
    </div>
  );
}
