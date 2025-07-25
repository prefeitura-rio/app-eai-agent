'use client';

import Link from 'next/link';
import { ThemeToggleButton } from '@/app/components/theme-toggle-button';
import { usePathname } from 'next/navigation';

export default function ExperimentsHeader() {
    const pathname = usePathname();
    const pathParts = pathname.split('/').filter(p => p);
    const datasetId = pathParts[1];

    return (
        <header className="container mx-auto px-4 sm:px-6 lg:px-8 py-4">
            <div className="flex justify-between items-center flex-wrap gap-3">
                <div>
                    <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Painel de Experimentos</h1>
                </div>
                <div className="flex items-center gap-2">
                    { (pathParts.length > 1) &&
                        <Link href={pathParts.length > 2 ? `/datasets/${datasetId}` : '/datasets'} className="px-3 py-2 border rounded-md border-gray-300 dark:border-gray-600">
                            Voltar
                        </Link>
                    }
                    <ThemeToggleButton />
                </div>
            </div>
        </header>
    );
}
