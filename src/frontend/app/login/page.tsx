'use client';

import { useState, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/app/contexts/AuthContext';
import { API_BASE_URL } from '@/app/components/config';

function LoginForm() {
  const [token, setToken] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    if (!token.trim()) {
      setError('Token cannot be empty.');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/auth?token=${token}`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error('Invalid token');
      }

      login(token);
      const redirectUrl = searchParams.get('redirect_url');
      router.push(redirectUrl || '/');
    } catch (err) {
      setError('Invalid token. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="max-w-md w-full bg-white dark:bg-gray-800 shadow-md rounded-lg p-8">
        <h1 className="text-2xl font-bold text-center text-gray-900 dark:text-white mb-6">Authentication</h1>
        <p className="text-center text-gray-600 dark:text-gray-400 mb-8">
          Please enter your Bearer Token to continue.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">Bearer Token</label>
            <textarea
              value={token}
              onChange={(e) => setToken(e.target.value)}
              className="mt-1 block w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 h-32"
              required
              placeholder="Paste your token here..."
            />
          </div>
          {error && <p className="text-red-500 text-sm text-center mb-4">{error}</p>}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {isLoading ? 'Validating...' : 'Submit Token'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <LoginForm />
    </Suspense>
  );
}