import React from 'react';
import { NavLink } from 'react-router-dom';
import { Activity, ShieldCheck, History, BarChart3, Users } from 'lucide-react';
import { useAuthStore } from '../../features/auth/auth-store';
import { hasPermission, Permission } from '../../features/auth/permissions';

export const Sidebar: React.FC = () => {
  const user = useAuthStore((state) => state.user);

  if (!user) return null;

  const navItems = [
    {
      to: '/dashboard',
      label: 'Dashboard',
      icon: <Activity size={20} />,
      permission: Permission.VIEW_DASHBOARD,
    },
    {
      to: '/inspection',
      label: 'Live Inspection',
      icon: <ShieldCheck size={20} />,
      permission: Permission.VIEW_INSPECTION,
    },
    {
      to: '/history',
      label: 'History',
      icon: <History size={20} />,
      permission: Permission.VIEW_HISTORY,
    },
    {
      to: '/analytics',
      label: 'Analytics',
      icon: <BarChart3 size={20} />,
      permission: Permission.VIEW_ANALYTICS,
    },
    {
      to: '/users',
      label: 'Users',
      icon: <Users size={20} />,
      permission: Permission.MANAGE_USERS,
    },
  ];

  return (
    <aside style={{
      width: '240px',
      backgroundColor: 'var(--color-bg-surface)',
      borderRight: '1px solid var(--color-border)',
      display: 'flex',
      flexDirection: 'column',
      height: '100vh',
      position: 'sticky',
      top: 0,
    }}>
      <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--color-border)' }}>
        <h2 style={{ fontSize: '1.2rem', fontWeight: '600', color: 'var(--color-primary)' }}>VisionQC</h2>
      </div>
      
      <nav style={{ padding: '1rem', display: 'flex', flexDirection: 'column', gap: '0.5rem', flex: 1 }}>
        {navItems.filter(item => hasPermission(user.role, item.permission)).map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            style={({ isActive }) => ({
              display: 'flex',
              alignItems: 'center',
              gap: '0.75rem',
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-md)',
              color: isActive ? 'var(--color-primary)' : 'var(--color-text-secondary)',
              backgroundColor: isActive ? 'var(--color-bg-base)' : 'transparent',
              fontWeight: isActive ? 600 : 400,
              transition: 'background 0.2s, color 0.2s',
            })}
          >
            {item.icon}
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
};
