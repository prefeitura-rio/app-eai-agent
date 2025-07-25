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
        <header className="">
            <div className="">
                <div>
                    <h1 className="">Painel de Experimentos</h1>
                </div>
                <div className="">
                    {pathname === '/experiments' && (
                        <Link href="/" className="">
                            Voltar
                        </Link>
                    )}
                    { (pathParts.length > 1) &&
                        <Link href={pathParts.length > 2 ? `/experiments/${datasetId}` : '/experiments'} className="">
                            Voltar
                        </Link>
                    }
                    <button onClick={toggleTheme} className="">
                        {theme === 'light' ? 'Dark' : 'Light'}
                    </button>
                    <button onClick={handleLogout} className="">
                        Sair
                    </button>
                </div>
            </div>
        </header>
    );
}
