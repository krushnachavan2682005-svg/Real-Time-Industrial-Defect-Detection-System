import React from 'react';
import type { InspectionResponse } from '../types';
import { DecisionBadge } from './DecisionBadge';
import { SeverityBadge } from './SeverityBadge';
import { DefectList } from './DefectList';
import { InspectionMetrics } from './InspectionMetrics';

interface Props {
  data: InspectionResponse;
}

export const InspectionResultPanel: React.FC<Props> = ({ data }) => {
  return (
    <div className="result-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
        <div>
          <h2 style={{ marginBottom: '0.5rem' }}>INSPECTION RESULT</h2>
          <DecisionBadge decision={data.decision} />
        </div>
        <div style={{ textAlign: 'right' }}>
          <div style={{ fontSize: '0.875rem', color: '#94a3b8', marginBottom: '0.25rem' }}>Severity</div>
          <SeverityBadge severity={data.severity} />
        </div>
      </div>

      <InspectionMetrics data={data} />
      
      <div style={{ marginTop: '2rem' }}>
        <h3 style={{ fontSize: '1.125rem', borderBottom: '1px solid #334155', paddingBottom: '0.5rem' }}>
          Detected Defects
        </h3>
        <DefectList defects={data.defects} />
      </div>
    </div>
  );
};
