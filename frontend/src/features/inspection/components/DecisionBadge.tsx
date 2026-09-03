import React from 'react';

interface Props {
  decision: string;
}

export const DecisionBadge: React.FC<Props> = ({ decision }) => {
  const d = decision.toUpperCase();
  let className = 'badge badge-decision-review';
  if (d === 'PASS') className = 'badge badge-decision-pass';
  else if (d === 'REJECT') className = 'badge badge-decision-reject';

  return <span className={className}>{d}</span>;
};
