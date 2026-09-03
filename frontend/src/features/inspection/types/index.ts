export interface BBox {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface DefectSchema {
  class_name: string;
  confidence: number;
  bbox: BBox;
  region: string;
}

export interface InspectionSummary {
  total_defects: number;
  affected_classes: string[];
}

export interface PLCDispatchInfo {
  enabled: boolean;
  dispatched: boolean;
  status?: string;
  message?: string;
}

export interface InspectionResponse {
  inspection_id: string;
  decision: string;
  severity: string;
  summary: InspectionSummary;
  defects: DefectSchema[];
  latency_ms: number;
  plc: PLCDispatchInfo;
}
