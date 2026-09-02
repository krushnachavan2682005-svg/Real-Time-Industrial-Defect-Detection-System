import { apiClient } from '../../../api/client';
import type { TokenResponse, AuthenticatedUser } from '../../../api/types/schemas';

export const login = async (username: string, password: string): Promise<TokenResponse> => {
  const params = new URLSearchParams();
  params.append('username', username);
  params.append('password', password);

  // FastAPI OAuth2PasswordRequestForm expects form-urlencoded
  const response = await apiClient.post<TokenResponse>('/api/v1/auth/login', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

export const getCurrentUser = async (): Promise<AuthenticatedUser> => {
  const response = await apiClient.get<AuthenticatedUser>('/api/v1/auth/me');
  return response.data;
};
