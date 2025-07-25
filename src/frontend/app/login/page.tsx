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
    <div className="">
      <div className="">
        <h1 className="">Authentication</h1>
        <p className="">
          Please enter your Bearer Token to continue.
        </p>
        <form onSubmit={handleSubmit}>
          <div className="">
            <label className="">Bearer Token</label>
            <textarea
              value={token}
              onChange={(e) => setToken(e.target.value)}
              className=""
              required
              placeholder="Paste your token here..."
            />
          </div>
          {error && <p className="">{error}</p>}
          <button
            type="submit"
            disabled={isLoading}
            className=""
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