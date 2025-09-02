-- NDC UK Backend Database Schema
-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================
-- 1. CORE TABLES
-- ==============================================

-- Chapters table
CREATE TABLE chapters (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  country text NOT NULL DEFAULT 'UK',
  description text,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Branches table  
CREATE TABLE branches (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  chapter_id uuid NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
  name text NOT NULL,
  location text NOT NULL,
  description text,
  min_members integer DEFAULT 20,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'pending')),
  created_by uuid REFERENCES auth.users(id),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  UNIQUE(chapter_id, name)
);

-- Role categories table for better organization
CREATE TABLE role_categories (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  description text,
  sort_order integer DEFAULT 0,
  created_at timestamp with time zone DEFAULT now()
);

-- Roles table
CREATE TABLE roles (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  scope_type text NOT NULL CHECK (scope_type IN ('chapter', 'branch', 'both')),
  category_id uuid REFERENCES role_categories(id),
  description text,
  permissions jsonb DEFAULT '{}',
  is_active boolean DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- User profiles (extends Supabase auth.users)
CREATE TABLE user_profiles (
  id uuid PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name text NOT NULL,
  phone text,
  address text,
  date_of_birth date,
  avatar_url text,
  membership_number text UNIQUE,
  status text NOT NULL DEFAULT 'not_approved' 
    CHECK (status IN ('not_approved', 'pending_approval', 'approved', 'suspended', 'expired')),
  email_verified boolean DEFAULT false,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Memberships (links users to branches)
CREATE TABLE memberships (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  branch_id uuid NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
  status text NOT NULL DEFAULT 'pending' 
    CHECK (status IN ('pending', 'active', 'lapsed', 'suspended')),
  joined_date timestamp with time zone DEFAULT now(),
  approved_by uuid REFERENCES auth.users(id),
  approved_at timestamp with time zone,
  card_issued boolean DEFAULT false,
  card_issued_at timestamp with time zone,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  UNIQUE(user_id, branch_id)
);

-- Executive assignments (handles role assignments)
CREATE TABLE executive_assignments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role_id uuid NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
  chapter_id uuid REFERENCES chapters(id),
  branch_id uuid REFERENCES branches(id),
  start_date timestamp with time zone NOT NULL DEFAULT now(),
  end_date timestamp with time zone,
  is_active boolean DEFAULT true,
  appointed_by uuid REFERENCES auth.users(id),
  notes text,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Ensure valid scope assignment
  CONSTRAINT valid_scope CHECK (
    (chapter_id IS NOT NULL AND branch_id IS NULL) OR 
    (chapter_id IS NULL AND branch_id IS NOT NULL) OR
    (chapter_id IS NOT NULL AND branch_id IS NOT NULL)
  )
);

-- ==============================================
-- 2. INDEXES FOR PERFORMANCE
-- ==============================================

CREATE INDEX idx_branches_chapter_id ON branches(chapter_id);
CREATE INDEX idx_branches_status ON branches(status);
CREATE INDEX idx_user_profiles_status ON user_profiles(status);
CREATE INDEX idx_user_profiles_membership_number ON user_profiles(membership_number);
CREATE INDEX idx_memberships_user_id ON memberships(user_id);
CREATE INDEX idx_memberships_branch_id ON memberships(branch_id);
CREATE INDEX idx_memberships_status ON memberships(status);
CREATE INDEX idx_executive_assignments_user_id ON executive_assignments(user_id);
CREATE INDEX idx_executive_assignments_role_id ON executive_assignments(role_id);
CREATE INDEX idx_executive_assignments_active ON executive_assignments(is_active);
CREATE INDEX idx_roles_scope_type ON roles(scope_type);
CREATE INDEX idx_roles_category_id ON roles(category_id);