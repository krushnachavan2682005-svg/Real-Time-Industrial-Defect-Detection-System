import React from 'react';
import type { DefectSchema } from '../types';
import { DefectCard } from './DefectCard';

interface Props {
  defects: DefectSchema[];
}

export const DefectList: React.FC<Props> = ({ defects }) => {
  if (!defects || defects.length === 0) {
    return <p style={{ color: '#94a3b8', marginTop: '1rem' }}>No defects detected.</p>;
  }

  return (
    <div className="defect-list">
      {defects.map((defect, idx) => (
        <DefectCard key={idx} defect={defect} index={idx} />
      ))}
    </div>
  );
};
