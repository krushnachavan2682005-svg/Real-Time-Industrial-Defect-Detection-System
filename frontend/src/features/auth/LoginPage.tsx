import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login, getCurrentUser } from './api/auth';
import { useAuthStore } from './auth-store';
import { setToken } from './token-storage';
import { Button } from '../../components/ui/Button';
import { Card } from '../../components/ui/Card';
import { ApiError } from '../../api/types/schemas';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const setUser = useAuthStore((state) => state.setUser);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      // 1. Authenticate and get token
      const tokenData = await login(username, password);
      setToken(tokenData.access_token);

      // 2. Fetch current user profile
      const user = await getCurrentUser();
      
      // 3. Update global store
      setUser(user);
      
      // 4. Redirect to dashboard
      navigate('/dashboard', { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      minHeight: '100vh',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '1rem',
      backgroundColor: 'var(--color-bg-base)'
    }}>
      <Card style={{ width: '100%', maxWidth: '400px' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 600, color: 'var(--color-primary)' }}>VisionQC</h1>
          <p style={{ color: 'var(--color-text-secondary)', marginTop: '0.5rem' }}>Sign in to continue</p>
        </div>

        {error && (
          <div style={{
            backgroundColor: 'var(--color-danger-bg)',
            color: 'var(--color-danger)',
            padding: '0.75rem',
            borderRadius: 'var(--radius-md)',
            marginBottom: '1rem',
            fontSize: '0.875rem'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label htmlFor="username" style={{ fontSize: '0.875rem', fontWeight: 500 }}>Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-bg-base)',
                color: 'var(--color-text-primary)',
                outline: 'none'
              }}
            />
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            <label htmlFor="password" style={{ fontSize: '0.875rem', fontWeight: 500 }}>Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              style={{
                width: '100%',
                padding: '0.75rem',
                borderRadius: 'var(--radius-md)',
                border: '1px solid var(--color-border)',
                backgroundColor: 'var(--color-bg-base)',
                color: 'var(--color-text-primary)',
                outline: 'none'
              }}
            />
          </div>

          <Button type="submit" isLoading={isLoading} style={{ marginTop: '0.5rem' }}>
            Sign In
          </Button>
        </form>
      </Card>
    </div>
  );
};
