import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  isLoading?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ 
  children, 
  variant = 'primary', 
  isLoading, 
  className = '', 
  disabled,
  ...props 
}) => {
  const baseStyle = {
    padding: '0.5rem 1rem',
    borderRadius: 'var(--radius-md)',
    fontWeight: 500,
    border: '1px solid transparent',
    transition: 'all 0.2s',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '0.5rem',
  };

  const variants = {
    primary: {
      backgroundColor: 'var(--color-primary)',
      color: 'white',
      borderColor: 'var(--color-primary)',
    },
    secondary: {
      backgroundColor: 'transparent',
      color: 'var(--color-text-primary)',
      borderColor: 'var(--color-border)',
    },
    danger: {
      backgroundColor: 'var(--color-danger)',
      color: 'white',
      borderColor: 'var(--color-danger)',
    }
  };

  return (
    <button
      disabled={isLoading || disabled}
      style={{
        ...baseStyle,
        ...variants[variant],
        opacity: (isLoading || disabled) ? 0.6 : 1,
        cursor: (isLoading || disabled) ? 'not-allowed' : 'pointer'
      }}
      className={className}
      {...props}
    >
      {isLoading ? <span className="loader">Wait...</span> : children}
    </button>
  );
};
