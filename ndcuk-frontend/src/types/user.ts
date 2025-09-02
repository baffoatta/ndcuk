import { User } from './auth';
import { RoleAssignment } from './role';

export interface UserProfile extends User {
  branch: {
    id: string;
    name: string;
    location: string;
  } | null;
  roles: RoleAssignment[];
  membership: {
    id: string;
    status: 'pending' | 'active' | 'lapsed' | 'suspended';
    joined_date: string;
    card_issued: boolean;
  } | null;
}

export interface UpdateUserRequest {
  full_name?: string;
  address?: string;
  gender?: string;
  occupation?: string;
  qualification?: string;
}

export interface UserListResponse {
  users: UserProfile[];
  total: number;
  page: number;
  size: number;
}

export interface UserStatusUpdate {
  status: User['status'];
  notes?: string;
}