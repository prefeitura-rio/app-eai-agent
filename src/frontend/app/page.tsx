import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
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
