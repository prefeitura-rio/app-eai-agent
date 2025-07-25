'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useAuth } from '@/app/contexts/AuthContext';

export default function ExperimentsHeader() {
    const pathname = usePathname();
    const router = useRouter();
    const { logout } = useAuth();
    const pathParts = pathname.split('/').filter(p => p);
    const datasetId = pathParts[1];
    const [theme, setTheme] = useState('light');

    useEffect(() => {
        const savedTheme = localStorage.getItem('theme') || 'light';
        setTheme(savedTheme);
        if (savedTheme === 'dark') {
            document.documentElement.classList.add('dark');
        }
    }, []);

    const toggleTheme = () => {
        const newTheme = theme === 'light' ? 'dark' : 'light';
        setTheme(newTheme);
        localStorage.setItem('theme', newTheme);
        if (newTheme === 'dark') {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    };

    const handleLogout = () => {
        logout();
        router.push(`/login?redirect_url=${pathname}`);
    };

    return (
        <header className="container mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center flex-wrap gap-3">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Painel de Experimentos</h1>
                </div>
                <div className="flex items-center gap-2">
                    { (pathParts.length > 1) &&
                        <Link href={pathParts.length > 2 ? `/experiments/${datasetId}` : '/experiments'} className="px-3 py-2 border rounded-md border-gray-300 dark:border-gray-600">
                            Voltar
                        </Link>
                    }
                    <button onClick={toggleTheme} className="px-3 py-2 border rounded-md border-gray-300 dark:border-gray-600">
                        {theme === 'light' ? 'Dark' : 'Light'}
                    </button>
                    <button onClick={handleLogout} className="px-3 py-2 border rounded-md border-red-500 text-red-500 hover:bg-red-500 hover:text-white">
                        Sair
                    </button>
                </div>
            </div>
        </header>
    );
}
