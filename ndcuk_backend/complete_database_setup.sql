-- ============================================================================
-- NDC UK Backend - Complete Database Setup Script
-- ============================================================================
-- Run this script in your Supabase SQL Editor to create all tables and data
-- Copy and paste this entire script into Supabase Dashboard > SQL Editor > New Query
-- ============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================
-- 1. CORE TABLES
-- ==============================================

-- Chapters table
CREATE TABLE IF NOT EXISTS chapters (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL,
  country text NOT NULL DEFAULT 'UK',
  description text,
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Role categories table for better organization
CREATE TABLE IF NOT EXISTS role_categories (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name text NOT NULL UNIQUE,
  description text,
  sort_order integer DEFAULT 0,
  created_at timestamp with time zone DEFAULT now()
);

-- Branches table  
CREATE TABLE IF NOT EXISTS branches (
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

-- Roles table
CREATE TABLE IF NOT EXISTS roles (
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
CREATE TABLE IF NOT EXISTS user_profiles (
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
CREATE TABLE IF NOT EXISTS memberships (
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
CREATE TABLE IF NOT EXISTS executive_assignments (
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

CREATE INDEX IF NOT EXISTS idx_branches_chapter_id ON branches(chapter_id);
CREATE INDEX IF NOT EXISTS idx_branches_status ON branches(status);
CREATE INDEX IF NOT EXISTS idx_user_profiles_status ON user_profiles(status);
CREATE INDEX IF NOT EXISTS idx_user_profiles_membership_number ON user_profiles(membership_number);
CREATE INDEX IF NOT EXISTS idx_memberships_user_id ON memberships(user_id);
CREATE INDEX IF NOT EXISTS idx_memberships_branch_id ON memberships(branch_id);
CREATE INDEX IF NOT EXISTS idx_memberships_status ON memberships(status);
CREATE INDEX IF NOT EXISTS idx_executive_assignments_user_id ON executive_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_executive_assignments_role_id ON executive_assignments(role_id);
CREATE INDEX IF NOT EXISTS idx_executive_assignments_active ON executive_assignments(is_active);
CREATE INDEX IF NOT EXISTS idx_roles_scope_type ON roles(scope_type);
CREATE INDEX IF NOT EXISTS idx_roles_category_id ON roles(category_id);

-- ==============================================
-- 3. SEED DATA
-- ==============================================

-- Insert role categories
INSERT INTO role_categories (name, description, sort_order) 
VALUES 
('Chapter Executives', 'Core chapter-level executive positions', 1),
('Branch Executives', 'Branch-level executive positions', 2),
('Committees', 'Chapter-level committee positions', 3),
('Special Roles', 'Special electoral and temporary roles', 4)
ON CONFLICT (name) DO NOTHING;

-- Insert default chapter
INSERT INTO chapters (name, country, description) VALUES 
('NDC UK & Ireland', 'UK', 'National Democratic Congress UK and Ireland Chapter')
ON CONFLICT DO NOTHING;

-- Get chapter ID for subsequent inserts
DO $$
DECLARE
    chapter_uuid uuid;
    category_chapter_exec uuid;
    category_branch_exec uuid;
    category_committees uuid;
    category_special uuid;
BEGIN
    -- Get chapter ID
    SELECT id INTO chapter_uuid FROM chapters WHERE name = 'NDC UK & Ireland';
    
    -- Get category IDs
    SELECT id INTO category_chapter_exec FROM role_categories WHERE name = 'Chapter Executives';
    SELECT id INTO category_branch_exec FROM role_categories WHERE name = 'Branch Executives';
    SELECT id INTO category_committees FROM role_categories WHERE name = 'Committees';
    SELECT id INTO category_special FROM role_categories WHERE name = 'Special Roles';
    
    -- Insert sample branches
    INSERT INTO branches (chapter_id, name, location, description) VALUES
    (chapter_uuid, 'London Central', 'London', 'Central London Branch'),
    (chapter_uuid, 'Manchester', 'Manchester', 'Manchester Branch'),
    (chapter_uuid, 'Birmingham', 'Birmingham', 'Birmingham Branch')
    ON CONFLICT (chapter_id, name) DO NOTHING;
    
    -- Insert Chapter-Level Executive Roles
    INSERT INTO roles (name, scope_type, description, permissions, category_id) VALUES
    ('Chairman', 'chapter', 'Chapter Chairman - Overall leadership and superuser privileges', '{"all": true}', category_chapter_exec),
    ('Vice Chairman', 'chapter', 'Chapter Vice Chairman - Deputy leadership', '{"chapter": ["read", "write"], "branches": ["read", "write"], "members": ["read", "write"]}', category_chapter_exec),
    ('Secretary', 'chapter', 'Chapter Secretary - Records, correspondence, committee creation', '{"chapter": ["read", "write"], "committees": ["create", "manage"], "members": ["read", "write"], "meetings": ["read", "write"]}', category_chapter_exec),
    ('Assistant Secretary', 'chapter', 'Chapter Assistant Secretary - Support role', '{"chapter": ["read"], "members": ["read", "write"], "meetings": ["read", "write"]}', category_chapter_exec),
    ('Treasurer', 'chapter', 'Chapter Treasurer - Financial management', '{"finance": ["read", "write"], "payments": ["read", "write"], "members": ["read"]}', category_chapter_exec),
    ('Assistant Treasurer', 'chapter', 'Chapter Assistant Treasurer - Financial support', '{"finance": ["read"], "payments": ["read"], "members": ["read"]}', category_chapter_exec),
    ('Organiser', 'chapter', 'Chapter Organiser - Events and mobilization', '{"events": ["read", "write"], "mobilization": ["read", "write"], "members": ["read"]}', category_chapter_exec),
    ('Deputy Organiser', 'chapter', 'Chapter Deputy Organiser - Support organizing', '{"events": ["read", "write"], "mobilization": ["read"], "members": ["read"]}', category_chapter_exec),
    ('Youth Organiser', 'chapter', 'Chapter Youth Organiser - Youth engagement', '{"events": ["read", "write"], "youth": ["read", "write"], "members": ["read"]}', category_chapter_exec),
    ('Deputy Youth Organiser', 'chapter', 'Chapter Deputy Youth Organiser - Youth support', '{"events": ["read"], "youth": ["read", "write"], "members": ["read"]}', category_chapter_exec),
    ('Women''s Organiser', 'chapter', 'Chapter Women''s Organiser - Women''s engagement', '{"events": ["read", "write"], "women": ["read", "write"], "members": ["read"]}', category_chapter_exec),
    ('Deputy Women''s Organiser', 'chapter', 'Chapter Deputy Women''s Organiser - Women''s support', '{"events": ["read"], "women": ["read", "write"], "members": ["read"]}', category_chapter_exec),
    ('Public Relations Officer (PRO)', 'chapter', 'Chapter PRO - Communications and publicity', '{"announcements": ["read", "write"], "press": ["read", "write"], "communications": ["read", "write"]}', category_chapter_exec),
    ('Deputy PRO', 'chapter', 'Chapter Deputy PRO - Communications support', '{"announcements": ["read"], "press": ["read"], "communications": ["read", "write"]}', category_chapter_exec),
    ('Welfare Officer', 'chapter', 'Chapter Welfare Officer - Member welfare and care', '{"welfare": ["read", "write"], "members": ["read", "write"], "events": ["read"]}', category_chapter_exec)
    ON CONFLICT (name) DO NOTHING;

    -- Insert Branch-Level Executive Roles
    INSERT INTO roles (name, scope_type, description, permissions, category_id) VALUES
    ('Branch Chairman', 'branch', 'Branch Chairman - Branch leadership and member approval', '{"branch": ["all"], "members": ["read", "write", "approve"], "events": ["read", "write"]}', category_branch_exec),
    ('Branch Secretary', 'branch', 'Branch Secretary - Branch records and correspondence', '{"branch": ["read", "write"], "members": ["read", "write", "approve"], "meetings": ["read", "write"]}', category_branch_exec),
    ('Branch Treasurer', 'branch', 'Branch Treasurer - Branch financial management', '{"branch_finance": ["read", "write"], "payments": ["read"], "members": ["read"]}', category_branch_exec),
    ('Branch Organiser', 'branch', 'Branch Organiser - Branch events and mobilization', '{"branch_events": ["read", "write"], "mobilization": ["read", "write"], "members": ["read"]}', category_branch_exec),
    ('Branch Youth Organiser', 'branch', 'Branch Youth Organiser - Branch youth engagement', '{"branch_events": ["read", "write"], "youth": ["read", "write"], "members": ["read"]}', category_branch_exec),
    ('Branch Women''s Organiser', 'branch', 'Branch Women''s Organiser - Branch women''s engagement', '{"branch_events": ["read", "write"], "women": ["read", "write"], "members": ["read"]}', category_branch_exec),
    ('Branch Welfare Officer', 'branch', 'Branch Welfare Officer - Branch member welfare', '{"welfare": ["read", "write"], "members": ["read", "write"], "branch_events": ["read"]}', category_branch_exec),
    ('Branch PRO', 'branch', 'Branch PRO - Branch communications (requires chapter approval)', '{"announcements": ["read", "draft"], "communications": ["read", "write"]}', category_branch_exec),
    ('Branch Executive Member', 'branch', 'Branch Executive Member - Special duties', '{"members": ["read"], "branch_events": ["read"], "meetings": ["read"]}', category_branch_exec)
    ON CONFLICT (name) DO NOTHING;

    -- Insert Committee Roles (Chapter Level)
    INSERT INTO roles (name, scope_type, description, permissions, category_id) VALUES
    ('Finance Committee Chair', 'chapter', 'Finance Committee Chairman', '{"finance": ["read", "write"], "committees": ["finance_committee"], "reports": ["read", "write"]}', category_committees),
    ('Finance Committee Member', 'chapter', 'Finance Committee Member', '{"finance": ["read"], "committees": ["finance_committee"], "reports": ["read"]}', category_committees),
    ('Public Relations Committee Chair', 'chapter', 'PR Committee Chairman', '{"pr": ["read", "write"], "committees": ["pr_committee"], "communications": ["read", "write"]}', category_committees),
    ('Public Relations Committee Member', 'chapter', 'PR Committee Member', '{"pr": ["read"], "committees": ["pr_committee"], "communications": ["read"]}', category_committees),
    ('Research Committee Chair', 'chapter', 'Research Committee Chairman', '{"research": ["read", "write"], "committees": ["research_committee"], "reports": ["read", "write"]}', category_committees),
    ('Research Committee Member', 'chapter', 'Research Committee Member', '{"research": ["read"], "committees": ["research_committee"], "reports": ["read"]}', category_committees),
    ('Organisation Committee Chair', 'chapter', 'Organisation Committee Chairman', '{"organisation": ["read", "write"], "committees": ["org_committee"], "mobilization": ["read", "write"]}', category_committees),
    ('Organisation Committee Member', 'chapter', 'Organisation Committee Member', '{"organisation": ["read"], "committees": ["org_committee"], "mobilization": ["read"]}', category_committees),
    ('Welfare Committee Chair', 'chapter', 'Welfare Committee Chairman', '{"welfare": ["read", "write"], "committees": ["welfare_committee"], "members": ["read", "write"]}', category_committees),
    ('Welfare Committee Member', 'chapter', 'Welfare Committee Member', '{"welfare": ["read"], "committees": ["welfare_committee"], "members": ["read"]}', category_committees),
    ('Complaints Committee Chair', 'chapter', 'Complaints Committee Chairman', '{"complaints": ["read", "write", "investigate"], "committees": ["complaints_committee"], "disciplinary": ["read"]}', category_committees),
    ('Complaints Committee Member', 'chapter', 'Complaints Committee Member', '{"complaints": ["read", "investigate"], "committees": ["complaints_committee"]}', category_committees),
    ('Disciplinary Committee Chair', 'chapter', 'Disciplinary Committee Chairman', '{"disciplinary": ["read", "write", "decide"], "committees": ["disciplinary_committee"], "members": ["suspend", "expel"]}', category_committees),
    ('Disciplinary Committee Member', 'chapter', 'Disciplinary Committee Member', '{"disciplinary": ["read", "decide"], "committees": ["disciplinary_committee"]}', category_committees),
    ('Audit Committee Chair', 'chapter', 'Audit Committee Chairman', '{"audit": ["read", "write"], "committees": ["audit_committee"], "finance": ["read", "audit"]}', category_committees),
    ('Audit Committee Member', 'chapter', 'Audit Committee Member', '{"audit": ["read"], "committees": ["audit_committee"], "finance": ["read"]}', category_committees)
    ON CONFLICT (name) DO NOTHING;

    -- Insert Special Electoral Role
    INSERT INTO roles (name, scope_type, description, permissions, category_id) VALUES
    ('Electoral Commissioner', 'both', 'Electoral Commissioner - Election supervision and management', 
     '{"elections": ["read", "write", "supervise"], "voting": ["manage"], "candidates": ["read", "write"], "electoral_roles": ["assign"]}', category_special)
    ON CONFLICT (name) DO NOTHING;
END
$$;

-- ==============================================
-- 4. DATABASE FUNCTIONS
-- ==============================================

-- Function to generate membership number
CREATE OR REPLACE FUNCTION generate_membership_number()
RETURNS TEXT AS $$
DECLARE
  new_number TEXT;
  counter INTEGER;
BEGIN
  -- Get current year
  SELECT EXTRACT(YEAR FROM NOW()) INTO counter;
  
  -- Generate format: NDC-YYYY-XXXX (e.g., NDC-2024-0001)
  SELECT 'NDC-' || counter || '-' || LPAD((
    SELECT COUNT(*) + 1 
    FROM user_profiles 
    WHERE membership_number IS NOT NULL
  )::TEXT, 4, '0') INTO new_number;
  
  RETURN new_number;
END;
$$ LANGUAGE plpgsql;

-- Function to handle user registration
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
  membership_num TEXT;
BEGIN
  -- Generate membership number
  SELECT generate_membership_number() INTO membership_num;
  
  -- Insert user profile
  INSERT INTO user_profiles (
    id, 
    full_name, 
    membership_number,
    email_verified
  )
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email),
    membership_num,
    NEW.email_confirmed_at IS NOT NULL
  );
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for new user registration
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

-- Function to update email verification status
CREATE OR REPLACE FUNCTION handle_email_verification()
RETURNS TRIGGER AS $$
BEGIN
  -- Update profile when email is verified
  IF NEW.email_confirmed_at IS NOT NULL AND OLD.email_confirmed_at IS NULL THEN
    UPDATE user_profiles 
    SET 
      email_verified = true,
      status = CASE 
        WHEN status = 'not_approved' THEN 'pending_approval'
        ELSE status 
      END,
      updated_at = NOW()
    WHERE id = NEW.id;
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger for email verification
DROP TRIGGER IF EXISTS on_auth_user_confirmed ON auth.users;
CREATE TRIGGER on_auth_user_confirmed
  AFTER UPDATE ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_email_verification();

-- Function to validate role assignments based on NDC rules
CREATE OR REPLACE FUNCTION validate_role_assignment(
  p_user_id uuid,
  p_role_id uuid,
  p_chapter_id uuid,
  p_branch_id uuid
) RETURNS boolean AS $$
DECLARE
  role_record RECORD;
  user_current_roles INTEGER;
  can_assign boolean := false;
BEGIN
  -- Get role details
  SELECT r.*, rc.name as category_name 
  INTO role_record 
  FROM roles r 
  JOIN role_categories rc ON r.category_id = rc.id 
  WHERE r.id = p_role_id;
  
  -- Check if role exists
  IF NOT FOUND THEN
    RETURN false;
  END IF;
  
  -- Count current active roles for user
  SELECT COUNT(*) INTO user_current_roles
  FROM executive_assignments
  WHERE user_id = p_user_id AND is_active = true;
  
  -- Business rules validation
  CASE role_record.scope_type
    WHEN 'chapter' THEN
      -- Chapter roles require chapter_id
      can_assign := (p_chapter_id IS NOT NULL);
    WHEN 'branch' THEN
      -- Branch roles require branch_id
      can_assign := (p_branch_id IS NOT NULL);
    WHEN 'both' THEN
      -- Both scope can be assigned at chapter or branch level
      can_assign := (p_chapter_id IS NOT NULL OR p_branch_id IS NOT NULL);
  END CASE;
  
  -- Additional validation rules can be added here
  -- e.g., limit on number of simultaneous roles, term limits, etc.
  
  RETURN can_assign;
END;
$$ LANGUAGE plpgsql;

-- Function to check assignment permissions
CREATE OR REPLACE FUNCTION can_assign_role(
  assigner_user_id uuid,
  target_user_id uuid,
  role_id uuid,
  target_chapter_id uuid DEFAULT NULL,
  target_branch_id uuid DEFAULT NULL
) RETURNS boolean AS $$
DECLARE
  assigner_roles RECORD;
  role_details RECORD;
BEGIN
  -- Get role being assigned
  SELECT * INTO role_details FROM roles WHERE id = role_id;
  
  -- Get assigner's current roles and permissions
  FOR assigner_roles IN
    SELECT r.*, ea.chapter_id, ea.branch_id
    FROM executive_assignments ea
    JOIN roles r ON ea.role_id = r.id
    WHERE ea.user_id = assigner_user_id AND ea.is_active = true
  LOOP
    -- Chapter Chairman can assign any role
    IF assigner_roles.name = 'Chairman' THEN
      RETURN true;
    END IF;
    
    -- Chapter Secretary can assign committee roles
    IF assigner_roles.name = 'Secretary' AND role_details.name LIKE '%Committee%' THEN
      RETURN true;
    END IF;
    
    -- Branch Chairman can assign branch-level roles in their branch
    IF assigner_roles.name = 'Branch Chairman' 
       AND role_details.scope_type IN ('branch', 'both')
       AND assigner_roles.branch_id = target_branch_id THEN
      RETURN true;
    END IF;
  END LOOP;
  
  RETURN false;
END;
$$ LANGUAGE plpgsql;

-- ==============================================
-- 5. ROW LEVEL SECURITY POLICIES
-- ==============================================

-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE executive_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE branches ENABLE ROW LEVEL SECURITY;
ALTER TABLE chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_categories ENABLE ROW LEVEL SECURITY;

-- USER PROFILES POLICIES
-- Users can view own profile
DROP POLICY IF EXISTS "Users can view own profile" ON user_profiles;
CREATE POLICY "Users can view own profile" ON user_profiles
  FOR SELECT USING (auth.uid() = id);

-- Users can update own profile
DROP POLICY IF EXISTS "Users can update own profile" ON user_profiles;
CREATE POLICY "Users can update own profile" ON user_profiles
  FOR UPDATE USING (auth.uid() = id);

-- Executives can view all profiles in their scope
DROP POLICY IF EXISTS "Executives can view member profiles" ON user_profiles;
CREATE POLICY "Executives can view member profiles" ON user_profiles
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM executive_assignments ea
      JOIN memberships m ON m.user_id = user_profiles.id
      WHERE ea.user_id = auth.uid() 
      AND ea.is_active = true
      AND (
        (ea.chapter_id IS NOT NULL) OR
        (ea.branch_id = m.branch_id)
      )
    )
  );

-- Chapter Chairman and Secretary can view all profiles
DROP POLICY IF EXISTS "Chapter leaders can view all profiles" ON user_profiles;
CREATE POLICY "Chapter leaders can view all profiles" ON user_profiles
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM executive_assignments ea
      JOIN roles r ON ea.role_id = r.id
      WHERE ea.user_id = auth.uid() 
      AND ea.is_active = true
      AND r.name IN ('Chairman', 'Secretary')
    )
  );

-- MEMBERSHIPS POLICIES
-- Users can view own memberships
DROP POLICY IF EXISTS "Users can view own memberships" ON memberships;
CREATE POLICY "Users can view own memberships" ON memberships
  FOR SELECT USING (auth.uid() = user_id);

-- Branch executives can manage branch memberships
DROP POLICY IF EXISTS "Branch executives can manage branch memberships" ON memberships;
CREATE POLICY "Branch executives can manage branch memberships" ON memberships
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM executive_assignments ea
      JOIN roles r ON ea.role_id = r.id
      WHERE ea.user_id = auth.uid() 
      AND ea.is_active = true
      AND ea.branch_id = memberships.branch_id
      AND r.name IN ('Branch Chairman', 'Branch Secretary')
    )
  );

-- Chapter leaders can manage all memberships
DROP POLICY IF EXISTS "Chapter leaders can manage all memberships" ON memberships;
CREATE POLICY "Chapter leaders can manage all memberships" ON memberships
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM executive_assignments ea
      JOIN roles r ON ea.role_id = r.id
      WHERE ea.user_id = auth.uid() 
      AND ea.is_active = true
      AND r.name IN ('Chairman', 'Secretary')
    )
  );

-- EXECUTIVE ASSIGNMENTS POLICIES
-- Users can view own assignments
DROP POLICY IF EXISTS "Users can view own assignments" ON executive_assignments;
CREATE POLICY "Users can view own assignments" ON executive_assignments
  FOR SELECT USING (auth.uid() = user_id);

-- Chapter Chairman can manage all assignments
DROP POLICY IF EXISTS "Chapter Chairman can manage all assignments" ON executive_assignments;
CREATE POLICY "Chapter Chairman can manage all assignments" ON executive_assignments
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM executive_assignments ea
      JOIN roles r ON ea.role_id = r.id
      WHERE ea.user_id = auth.uid() 
      AND ea.is_active = true
      AND r.name = 'Chairman'
    )
  );

-- Chapter Secretary can manage committee assignments
DROP POLICY IF EXISTS "Chapter Secretary can manage committee assignments" ON executive_assignments;
CREATE POLICY "Chapter Secretary can manage committee assignments" ON executive_assignments
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM executive_assignments ea
      JOIN roles r ON ea.role_id = r.id
      JOIN roles target_r ON executive_assignments.role_id = target_r.id
      WHERE ea.user_id = auth.uid() 
      AND ea.is_active = true
      AND r.name = 'Secretary'
      AND target_r.name LIKE '%Committee%'
    )
  );

-- Branch Chairman can manage branch assignments
DROP POLICY IF EXISTS "Branch Chairman can manage branch assignments" ON executive_assignments;
CREATE POLICY "Branch Chairman can manage branch assignments" ON executive_assignments
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM executive_assignments ea
      JOIN roles r ON ea.role_id = r.id
      WHERE ea.user_id = auth.uid() 
      AND ea.is_active = true
      AND r.name = 'Branch Chairman'
      AND ea.branch_id = executive_assignments.branch_id
    )
  );

-- BRANCHES POLICIES
-- Everyone can view active branches
DROP POLICY IF EXISTS "Everyone can view active branches" ON branches;
CREATE POLICY "Everyone can view active branches" ON branches
  FOR SELECT USING (status = 'active');

-- Chapter leaders can manage all branches
DROP POLICY IF EXISTS "Chapter leaders can manage branches" ON branches;
CREATE POLICY "Chapter leaders can manage branches" ON branches
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM executive_assignments ea
      JOIN roles r ON ea.role_id = r.id
      WHERE ea.user_id = auth.uid() 
      AND ea.is_active = true
      AND r.name IN ('Chairman', 'Secretary')
    )
  );

-- Branch executives can update their own branch
DROP POLICY IF EXISTS "Branch executives can update own branch" ON branches;
CREATE POLICY "Branch executives can update own branch" ON branches
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM executive_assignments ea
      JOIN roles r ON ea.role_id = r.id
      WHERE ea.user_id = auth.uid() 
      AND ea.is_active = true
      AND ea.branch_id = branches.id
      AND r.scope_type IN ('branch', 'both')
    )
  );

-- CHAPTERS POLICIES
-- Everyone can view active chapters
DROP POLICY IF EXISTS "Everyone can view active chapters" ON chapters;
CREATE POLICY "Everyone can view active chapters" ON chapters
  FOR SELECT USING (status = 'active');

-- Only Chapter Chairman can manage chapters
DROP POLICY IF EXISTS "Chapter Chairman can manage chapters" ON chapters;
CREATE POLICY "Chapter Chairman can manage chapters" ON chapters
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM executive_assignments ea
      JOIN roles r ON ea.role_id = r.id
      WHERE ea.user_id = auth.uid() 
      AND ea.is_active = true
      AND r.name = 'Chairman'
    )
  );

-- ROLES AND ROLE CATEGORIES POLICIES
-- Everyone can view active roles and categories (needed for registration)
DROP POLICY IF EXISTS "Everyone can view active roles" ON roles;
CREATE POLICY "Everyone can view active roles" ON roles
  FOR SELECT USING (is_active = true);

DROP POLICY IF EXISTS "Everyone can view role categories" ON role_categories;
CREATE POLICY "Everyone can view role categories" ON role_categories
  FOR SELECT USING (true);

-- Only Chapter Chairman and Secretary can manage roles
DROP POLICY IF EXISTS "Chapter leaders can manage roles" ON roles;
CREATE POLICY "Chapter leaders can manage roles" ON roles
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM executive_assignments ea
      JOIN roles r ON ea.role_id = r.id
      WHERE ea.user_id = auth.uid() 
      AND ea.is_active = true
      AND r.name IN ('Chairman', 'Secretary')
    )
  );

DROP POLICY IF EXISTS "Chapter leaders can manage role categories" ON role_categories;
CREATE POLICY "Chapter leaders can manage role categories" ON role_categories
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM executive_assignments ea
      JOIN roles r ON ea.role_id = r.id
      WHERE ea.user_id = auth.uid() 
      AND ea.is_active = true
      AND r.name IN ('Chairman', 'Secretary')
    )
  );

-- ==============================================
-- 6. FINAL SETUP VERIFICATION
-- ==============================================

-- Display setup summary
DO $$
DECLARE
    table_count INTEGER;
    role_count INTEGER;
    branch_count INTEGER;
BEGIN
    -- Count tables
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name IN ('chapters', 'branches', 'roles', 'role_categories', 'user_profiles', 'memberships', 'executive_assignments');
    
    -- Count roles
    SELECT COUNT(*) INTO role_count FROM roles;
    
    -- Count branches  
    SELECT COUNT(*) INTO branch_count FROM branches;
    
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'NDC UK Backend Database Setup Complete!';
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Tables created: %', table_count;
    RAISE NOTICE 'Roles inserted: %', role_count;
    RAISE NOTICE 'Branches created: %', branch_count;
    RAISE NOTICE '============================================================================';
    RAISE NOTICE 'Your NDC UK Backend is now ready to use!';
    RAISE NOTICE 'Start your FastAPI server: uvicorn app.main:app --reload';
    RAISE NOTICE 'API Documentation: http://localhost:8000/docs';
    RAISE NOTICE '============================================================================';
END
$$;