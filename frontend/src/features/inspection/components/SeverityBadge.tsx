import React from 'react';

interface Props {
  severity: string;
}

export const SeverityBadge: React.FC<Props> = ({ severity }) => {
  const s = severity.toUpperCase();
  let className = 'badge badge-severity-none';
  if (s === 'LOW') className = 'badge badge-severity-low';
  else if (s === 'MEDIUM') className = 'badge badge-severity-medium';
  else if (s === 'HIGH') className = 'badge badge-severity-high';
  else if (s === 'CRITICAL') className = 'badge badge-severity-critical';

  return <span className={className}>{s}</span>;
};
