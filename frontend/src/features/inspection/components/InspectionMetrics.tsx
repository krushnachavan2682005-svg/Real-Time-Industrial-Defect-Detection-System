import React from 'react';
import type { InspectionResponse } from '../types';

interface Props {
  data: InspectionResponse;
}

export const InspectionMetrics: React.FC<Props> = ({ data }) => {
  const { summary, latency_ms, plc } = data;

  return (
    <div className="metrics-grid">
      <div className="metric-item">
        <div className="metric-label">Total Defects</div>
        <div className="metric-value">{summary.total_defects}</div>
      </div>
      <div className="metric-item">
        <div className="metric-label">Pipeline Latency</div>
        <div className="metric-value">{latency_ms.toFixed(1)} ms</div>
      </div>
      <div className="metric-item" style={{ gridColumn: '1 / -1' }}>
        <div className="metric-label">PLC Status</div>
        <div className="metric-value" style={{ fontSize: '1rem', fontWeight: 500 }}>
          {plc.enabled 
            ? `Enabled: ${plc.dispatched ? 'Command Sent' : 'No Command'} - ${plc.status || 'N/A'}`
            : 'Disabled'}
        </div>
      </div>
    </div>
  );
};
