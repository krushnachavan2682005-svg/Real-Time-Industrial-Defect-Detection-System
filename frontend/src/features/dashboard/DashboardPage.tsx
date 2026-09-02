import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../../api/client';
import type { HealthResponse } from '../../api/types/schemas';
import { Card } from '../../components/ui/Card';
import { useAuthStore } from '../auth/auth-store';

export const DashboardPage: React.FC = () => {
  const user = useAuthStore((state) => state.user);

  const { data: health, isLoading, isError } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      const { data } = await apiClient.get<HealthResponse>('/health');
      return data;
    },
    refetchInterval: 30000, // Poll every 30 seconds
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      <header>
        <h1 style={{ fontSize: '1.8rem', fontWeight: 600, color: 'var(--color-text-primary)', marginBottom: '0.5rem' }}>
          Welcome back, {user?.username}
        </h1>
        <p style={{ color: 'var(--color-text-secondary)' }}>System overview and health metrics.</p>
      </header>

      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
        <Card>
          <h3 style={{ fontSize: '1rem', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>API Connectivity</h3>
          {isLoading ? (
            <div style={{ color: 'var(--color-text-muted)' }}>Checking...</div>
          ) : isError ? (
            <div style={{ color: 'var(--color-danger)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--color-danger)' }}></span>
              Offline
            </div>
          ) : (
            <div style={{ color: 'var(--color-success)', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: 'var(--color-success)' }}></span>
              {health?.status === 'healthy' ? 'Operational' : 'Degraded'}
            </div>
          )}
        </Card>

        <Card>
          <h3 style={{ fontSize: '1rem', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>Inference Engine</h3>
          <div style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>
            {health?.model_loaded ? 'Model Loaded' : 'Waiting...'}
          </div>
        </Card>

        <Card>
          <h3 style={{ fontSize: '1rem', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>PLC Status</h3>
          <div style={{ fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'capitalize' }}>
            {health?.plc_mode || 'Unknown'}
          </div>
        </Card>

        <Card>
          <h3 style={{ fontSize: '1rem', color: 'var(--color-text-secondary)', marginBottom: '0.5rem' }}>Database</h3>
          <div style={{ fontWeight: 600, color: 'var(--color-text-primary)', textTransform: 'capitalize' }}>
            {health?.database || 'Unknown'}
          </div>
        </Card>
      </section>

      <section>
        <Card style={{ padding: '3rem', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: 'var(--color-bg-base)', borderStyle: 'dashed' }}>
          <div style={{ textAlign: 'center', color: 'var(--color-text-muted)' }}>
            <p style={{ marginBottom: '0.5rem' }}>Analytics & Live Inspection Modules</p>
            <p style={{ fontSize: '0.875rem' }}>To be implemented in future modules.</p>
          </div>
        </Card>
      </section>
    </div>
  );
};
