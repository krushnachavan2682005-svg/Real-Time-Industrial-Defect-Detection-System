import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../../features/auth/auth-store';
import { Permission, hasPermission } from '../../features/auth/permissions';

interface RoleGuardProps {
  permission: Permission;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({ permission }) => {
  const { user, isInitializing } = useAuthStore();

  if (isInitializing) {
    return null; // Let ProtectedRoute handle loader
  }

  if (!user || !hasPermission(user.role, permission)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <Outlet />;
};
