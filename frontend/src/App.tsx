import React, { useEffect } from 'react';
import { BrowserRouter } from 'react-router-dom';
import { QueryProvider } from './app/providers/QueryProvider';
import { AppRouter } from './app/router';
import { useAuthStore } from './features/auth/auth-store';
import { getToken } from './features/auth/token-storage';
import { getCurrentUser } from './features/auth/api/auth';

const App: React.FC = () => {
  const { setUser, setInitializing } = useAuthStore();

  useEffect(() => {
    const initAuth = async () => {
      const token = getToken();
      if (!token) {
        setInitializing(false);
        return;
      }

      try {
        const user = await getCurrentUser();
        setUser(user);
      } catch (err) {
        console.error('Failed to restore session', err);
        setInitializing(false);
      }
    };

    initAuth();
  }, [setUser, setInitializing]);

  useEffect(() => {
    const handleUnauthorized = () => {
      // The interceptor dispatches this event when a 401 occurs
      useAuthStore.getState().logout();
    };

    window.addEventListener('unauthorized', handleUnauthorized);
    return () => window.removeEventListener('unauthorized', handleUnauthorized);
  }, []);

  return (
    <QueryProvider>
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </QueryProvider>
  );
};

export default App;
