import React from 'react';
import { useAuthStore } from '../../features/auth/auth-store';
import { LogOut, User } from 'lucide-react';
import { Button } from '../ui/Button';
import { useNavigate } from 'react-router-dom';

export const Topbar: React.FC = () => {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header style={{
      height: '64px',
      backgroundColor: 'var(--color-bg-surface)',
      borderBottom: '1px solid var(--color-border)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'flex-end',
      padding: '0 1.5rem',
      position: 'sticky',
      top: 0,
      zIndex: 10,
    }}>
      {user && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              backgroundColor: 'var(--color-bg-base)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--color-primary)'
            }}>
              <User size={18} />
            </div>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <span style={{ fontSize: '0.875rem', fontWeight: 500, lineHeight: 1 }}>{user.username}</span>
              <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{user.role}</span>
            </div>
          </div>
          
          <Button variant="secondary" onClick={handleLogout} style={{ padding: '0.4rem 0.75rem', fontSize: '0.875rem' }}>
            <LogOut size={16} /> Logout
          </Button>
        </div>
      )}
    </header>
  );
};
