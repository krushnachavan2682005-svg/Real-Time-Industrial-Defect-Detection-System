import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../../features/auth/auth-store';

export const PublicRoute: React.FC = () => {
  const { isAuthenticated, isInitializing } = useAuthStore();

  if (isInitializing) {
    return null;
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Outlet />;
};
