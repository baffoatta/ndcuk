import { apiClient } from './client';
import { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  User, 
  RefreshTokenRequest,
  RegistrationInfo
} from '@/types/auth';

export const authApi = {
  // GET /auth/registration-info
  getRegistrationInfo: async (): Promise<RegistrationInfo> => {
    return apiClient.get('/auth/registration-info');
  },

  // POST /auth/login
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    return apiClient.post('/auth/login', credentials);
  },

  // POST /auth/register  
  register: async (userData: RegisterRequest): Promise<{ message: string; user_id: string; membership_number: string; branch_name: string; email_confirmed: boolean }> => {
    return apiClient.post('/auth/register', userData);
  },

  // POST /auth/social-login
  socialLogin: async (provider: string, token: string): Promise<AuthResponse> => {
    return apiClient.post('/auth/social-login', { provider, token });
  },

  // POST /auth/refresh
  refreshToken: async (refreshData: RefreshTokenRequest): Promise<AuthResponse> => {
    return apiClient.post('/auth/refresh', refreshData);
  },

  // POST /auth/logout
  logout: async (): Promise<void> => {
    return apiClient.post('/auth/logout');
  },

  // POST /auth/verify-email
  verifyEmail: async (token: string): Promise<{ message: string }> => {
    return apiClient.post('/auth/verify-email', { token });
  },

  // POST /auth/forgot-password
  forgotPassword: async (email: string): Promise<{ message: string }> => {
    return apiClient.post('/auth/forgot-password', { email });
  },

  // POST /auth/reset-password
  resetPassword: async (token: string, password: string): Promise<{ message: string }> => {
    return apiClient.post('/auth/reset-password', { token, password });
  },

  // GET /auth/me
  getCurrentUser: async (): Promise<User> => {
    return apiClient.get('/auth/me');
  },
};