import React from 'react';
import type { DefectSchema } from '../types';

interface Props {
  defect: DefectSchema;
  index: number;
}

export const DefectCard: React.FC<Props> = ({ defect, index }) => {
  const { class_name, confidence, bbox, region } = defect;

  return (
    <div className="defect-card">
      <div className="defect-card-header">
        <span className="defect-class">Defect #{index + 1}: {class_name}</span>
        <span className="defect-conf">{(confidence * 100).toFixed(1)}%</span>
      </div>
      <div className="defect-details">
        <span>Region: {region || 'UNKNOWN'}</span>
        <span>
          Box: [{bbox.x1}, {bbox.y1}] → [{bbox.x2}, {bbox.y2}]
        </span>
      </div>
    </div>
  );
};
