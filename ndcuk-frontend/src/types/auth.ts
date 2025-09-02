export interface User {
  id: string;
  email: string;
  full_name: string;
  address: string;
  date_of_birth: string;
  gender?: string;
  occupation?: string;
  qualification?: string;
  avatar_url?: string;
  membership_number?: string;
  status: 'not_approved' | 'pending_approval' | 'approved' | 'suspended' | 'expired';
  email_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
  gender: string;
  date_of_birth: string;
  occupation: string;
  qualification: string;
  address: string;
  branch_name: string;
  profile_picture?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user?: User;
}

export interface RefreshTokenRequest {
  refresh_token: string;
}

export interface RegistrationInfo {
  available_branches: string[];
  gender_options: string[];
  qualification_categories: string[];
  password_requirements: {
    min_length: number;
    required: string[];
  };
  age_requirement: {
    minimum_age: number;
  };
}