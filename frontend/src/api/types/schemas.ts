// Role enum mapped from backend
export const Role = {
  ADMIN: 'ADMIN',
  ENGINEER: 'ENGINEER',
  OPERATOR: 'OPERATOR',
  VIEWER: 'VIEWER',
} as const;
export type Role = (typeof Role)[keyof typeof Role];

// User Models
export interface UserResponse {
  id: number;
  username: string;
  role: Role;
  is_active: boolean;
}

export interface AuthenticatedUser extends UserResponse {}

// Token Models
export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

// Health Models
export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  plc_mode: string;
  database?: string;
}

// Error Schema
export interface ErrorDetail {
  code: string;
  message: string;
}

export interface ErrorResponse {
  error: ErrorDetail;
}

// Generic API Error class
export class ApiError extends Error {
  public statusCode: number;
  public details?: ErrorDetail;

  constructor(message: string, statusCode: number, details?: ErrorDetail) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.details = details;
  }
}
