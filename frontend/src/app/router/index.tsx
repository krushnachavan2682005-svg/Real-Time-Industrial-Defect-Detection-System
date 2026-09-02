import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

import { ProtectedRoute } from './ProtectedRoute';
import { PublicRoute } from './PublicRoute';
import { RoleGuard } from './RoleGuard';
import { AppLayout } from '../../components/layout/AppLayout';

import { LoginPage } from '../../features/auth/LoginPage';
import { DashboardPage } from '../../features/dashboard/DashboardPage';
import { NotFoundPage } from '../../pages/NotFoundPage';
import { UnauthorizedPage } from '../../pages/UnauthorizedPage';

import { Permission } from '../../features/auth/permissions';

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      <Route element={<PublicRoute />}>
        <Route path="/login" element={<LoginPage />} />
      </Route>

      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          
          <Route element={<RoleGuard permission={Permission.VIEW_DASHBOARD} />}>
            <Route path="/dashboard" element={<DashboardPage />} />
          </Route>

          {/* Placeholders for future modules */}
          <Route element={<RoleGuard permission={Permission.VIEW_INSPECTION} />}>
            <Route path="/inspection" element={<div>Live Inspection Placeholder</div>} />
          </Route>
          
          <Route element={<RoleGuard permission={Permission.VIEW_HISTORY} />}>
            <Route path="/history" element={<div>Inspection History Placeholder</div>} />
          </Route>

          <Route element={<RoleGuard permission={Permission.VIEW_ANALYTICS} />}>
            <Route path="/analytics" element={<div>Analytics Placeholder</div>} />
          </Route>

          <Route element={<RoleGuard permission={Permission.MANAGE_USERS} />}>
            <Route path="/users" element={<div>Users Management Placeholder</div>} />
          </Route>

          <Route path="/unauthorized" element={<UnauthorizedPage />} />
        </Route>
      </Route>

      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
};
