import { apiClient } from './client';
import { 
  Branch, 
  CreateBranchRequest, 
  UpdateBranchRequest,
  BranchMember,
  BranchStats 
} from '@/types/branch';

export const branchesApi = {
  // GET /branches/public (public endpoint for registration)
  getPublicBranches: async (): Promise<Branch[]> => {
    return apiClient.get('/branches/public');
  },

  // GET /branches/
  getBranches: async (): Promise<Branch[]> => {
    return apiClient.get('/branches/');
  },

  // POST /branches/
  createBranch: async (data: CreateBranchRequest): Promise<Branch> => {
    return apiClient.post('/branches/', data);
  },

  // GET /branches/{branch_id}
  getBranchById: async (branchId: string): Promise<Branch> => {
    return apiClient.get(`/branches/${branchId}`);
  },

  // PUT /branches/{branch_id}
  updateBranch: async (branchId: string, data: UpdateBranchRequest): Promise<Branch> => {
    return apiClient.put(`/branches/${branchId}`, data);
  },

  // GET /branches/{branch_id}/members
  getBranchMembers: async (branchId: string, params?: {
    status?: string;
    page?: number;
    limit?: number;
  }): Promise<BranchMember[]> => {
    return apiClient.get(`/branches/${branchId}/members`, { params });
  },

  // PUT /branches/{branch_id}/members/{user_id}/approve
  approveBranchMember: async (branchId: string, userId: string): Promise<{ message: string }> => {
    return apiClient.put(`/branches/${branchId}/members/${userId}/approve`);
  },

  // GET /branches/{branch_id}/stats
  getBranchStats: async (branchId: string): Promise<BranchStats> => {
    return apiClient.get(`/branches/${branchId}/stats`);
  },

  // GET /branches/my-branches
  getMyBranches: async (): Promise<Branch[]> => {
    return apiClient.get('/branches/my-branches');
  },

  // POST /branches/{branch_id}/members/{user_id}/issue-card
  issueMembershipCard: async (branchId: string, userId: string): Promise<{ message: string }> => {
    return apiClient.post(`/branches/${branchId}/members/${userId}/issue-card`);
  },
};