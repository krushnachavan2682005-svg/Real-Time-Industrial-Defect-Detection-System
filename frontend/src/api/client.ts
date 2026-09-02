import axios from 'axios';
import { env } from '../app/config/env';
import { ApiError } from './types/schemas';
import { getToken, removeToken } from '../features/auth/token-storage';

export const apiClient = axios.create({
  baseURL: env.API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor
apiClient.interceptors.request.use(
  (config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response Interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with a status other than 200 range
      const status = error.response.status;
      const data = error.response.data;

      if (status === 401) {
        // Unauthorized - Clear token and redirect to login
        removeToken();
        window.dispatchEvent(new Event('unauthorized'));
      }

      // Format standard error
      throw new ApiError(
        data.detail || data.message || 'An error occurred',
        status,
        data.error
      );
    } else if (error.request) {
      // Network Error
      throw new ApiError('Network Error. Please check your connection.', 0);
    } else {
      // Unexpected error
      throw new ApiError(error.message, 0);
    }
  }
);
