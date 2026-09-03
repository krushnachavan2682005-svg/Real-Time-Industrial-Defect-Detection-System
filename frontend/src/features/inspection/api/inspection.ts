import { apiClient } from '../../../api/client';
import type { InspectionResponse } from '../types';

export const inspectImage = async (file: File): Promise<InspectionResponse> => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post<InspectionResponse>('/api/v1/inspect', formData, {
    headers: {
      'Content-Type': undefined
    }
  });

  return response.data;
};
