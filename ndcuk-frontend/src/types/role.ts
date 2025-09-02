import { User } from './auth';

export interface Role {
  id: string;
  name: string;
  scope_type: 'chapter' | 'branch' | 'both';
  description?: string;
  permissions: Record<string, any>;
  is_active: boolean;
  category: {
    id: string;
    name: string;
    description: string;
  };
  created_at: string;
  updated_at: string;
}

export interface RoleAssignment {
  id: string;
  user_id: string;
  role: Role;
  chapter: {
    id: string;
    name: string;
  } | null;
  branch: {
    id: string;
    name: string;
    location: string;
  } | null;
  start_date: string;
  end_date?: string;
  is_active: boolean;
  appointed_by: {
    id: string;
    full_name: string;
  } | null;
  notes?: string;
  created_at: string;
}

export interface CreateRoleAssignmentRequest {
  user_id: string;
  role_id: string;
  chapter_id?: string;
  branch_id?: string;
  start_date?: string;
  notes?: string;
}

export interface UpdateRoleAssignmentRequest {
  end_date?: string;
  is_active?: boolean;
  notes?: string;
}

export interface RoleAssignmentResponse {
  assignments: RoleAssignment[];
  total: number;
}