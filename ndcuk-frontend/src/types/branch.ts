import { User } from './auth';
import { RoleAssignment } from './role';

export interface Branch {
  id: string;
  chapter_id: string;
  name: string;
  location: string;
  description?: string;
  min_members: number;
  status: 'active' | 'inactive' | 'pending';
  created_by: {
    id: string;
    full_name: string;
  } | null;
  member_count: number;
  executives: RoleAssignment[];
  created_at: string;
  updated_at: string;
}

export interface CreateBranchRequest {
  name: string;
  location: string;
  description?: string;
  min_members?: number;
}

export interface UpdateBranchRequest {
  name?: string;
  location?: string;
  description?: string;
  min_members?: number;
  status?: Branch['status'];
}

export interface BranchMember {
  id: string;
  user: User;
  status: 'pending' | 'active' | 'lapsed' | 'suspended';
  joined_date: string;
  approved_by: {
    id: string;
    full_name: string;
  } | null;
  approved_at?: string;
  card_issued: boolean;
  card_issued_at?: string;
}

export interface BranchStats {
  total_members: number;
  active_members: number;
  pending_members: number;
  suspended_members: number;
  executives_count: number;
  membership_growth: {
    period: string;
    growth_rate: number;
    new_members: number;
  };
}