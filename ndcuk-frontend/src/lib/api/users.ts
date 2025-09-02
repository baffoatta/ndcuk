import { apiClient } from './client';
import { 
  User, 
  UserProfile, 
  UpdateUserRequest, 
  UserListResponse,
  UserStatusUpdate 
} from '@/types/user';

export const usersApi = {
  // GET /users/me (actually /auth/me in our backend)
  getCurrentUser: async (): Promise<UserProfile> => {
    return apiClient.get('/auth/me');
  },

  // PUT /users/me
  updateProfile: async (data: UpdateUserRequest): Promise<UserProfile> => {
    return apiClient.put('/users/me', data);
  },

  // GET /users/
  getUsers: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
    branch_id?: string;
    status?: string;
  }): Promise<UserListResponse> => {
    return apiClient.get('/users/', { params });
  },

  // GET /users/{user_id}
  getUserById: async (userId: string): Promise<UserProfile> => {
    return apiClient.get(`/users/${userId}`);
  },

  // PUT /users/{user_id}/approve
  approveUser: async (userId: string): Promise<{ message: string }> => {
    return apiClient.put(`/users/${userId}/approve`);
  },

  // PUT /users/{user_id}/status
  updateUserStatus: async (userId: string, status: UserStatusUpdate): Promise<UserProfile> => {
    return apiClient.put(`/users/${userId}/status`, status);
  },

  // POST /users/{user_id}/avatar
  uploadAvatar: async (userId: string, file: File): Promise<{ avatar_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post(`/users/${userId}/avatar`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};