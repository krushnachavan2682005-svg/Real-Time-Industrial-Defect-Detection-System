import { useMutation } from '@tanstack/react-query';
import { inspectImage } from '../api/inspection';
import type { InspectionResponse } from '../types';
import { ApiError } from '../../../api/types/schemas';

export const useInspection = () => {
  return useMutation<InspectionResponse, ApiError, File>({
    mutationFn: (file: File) => inspectImage(file),
  });
};
