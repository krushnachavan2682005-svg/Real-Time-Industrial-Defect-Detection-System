import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';

export const UnauthorizedPage: React.FC = () => {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      minHeight: '100vh',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '2rem',
      textAlign: 'center'
    }}>
      <h1 style={{ fontSize: '4rem', fontWeight: 700, color: 'var(--color-warning)', marginBottom: '1rem' }}>403</h1>
      <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem' }}>Access Denied</h2>
      <p style={{ color: 'var(--color-text-secondary)', marginBottom: '2rem' }}>
        You do not have the required permissions to view this page.
      </p>
      <Link to="/dashboard">
        <Button>Return to Dashboard</Button>
      </Link>
    </div>
  );
};
