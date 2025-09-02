-- NDC UK Backend Row Level Security Policies
-- Enable RLS on all tables
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE memberships ENABLE ROW LEVEL SECURITY;
ALTER TABLE executive_assignments ENABLE ROW LEVEL SECURITY;
ALTER TABLE branches ENABLE ROW LEVEL SECURITY;
ALTER TABLE chapters ENABLE ROW LEVEL SECURITY;
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
ALTER TABLE role_categories ENABLE ROW LEVEL SECURITY;

-- ==============================================
-- USER PROFILES POLICIES
-- ==============================================

-- Users can view own profile
CREATE POLICY "Users can view own profile" ON user_profiles
  FOR SELECT USING (auth.uid() = id);

-- Users can update own profile
CREATE POLICY "Users can update own profile" ON user_profiles
  FOR UPDATE USING (auth.uid() = id);

-- Executives can view all profiles in their scope
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

-- ==============================================
-- MEMBERSHIPS POLICIES
-- ==============================================

-- Users can view own memberships
CREATE POLICY "Users can view own memberships" ON memberships
  FOR SELECT USING (auth.uid() = user_id);

-- Branch executives can manage branch memberships
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

-- ==============================================
-- EXECUTIVE ASSIGNMENTS POLICIES
-- ==============================================

-- Users can view own assignments
CREATE POLICY "Users can view own assignments" ON executive_assignments
  FOR SELECT USING (auth.uid() = user_id);

-- Chapter Chairman can manage all assignments
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

-- ==============================================
-- BRANCHES POLICIES
-- ==============================================

-- Everyone can view active branches
CREATE POLICY "Everyone can view active branches" ON branches
  FOR SELECT USING (status = 'active');

-- Chapter leaders can manage all branches
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

-- ==============================================
-- CHAPTERS POLICIES
-- ==============================================

-- Everyone can view active chapters
CREATE POLICY "Everyone can view active chapters" ON chapters
  FOR SELECT USING (status = 'active');

-- Only Chapter Chairman can manage chapters
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

-- ==============================================
-- ROLES AND ROLE CATEGORIES POLICIES
-- ==============================================

-- Everyone can view active roles and categories (needed for registration)
CREATE POLICY "Everyone can view active roles" ON roles
  FOR SELECT USING (is_active = true);

CREATE POLICY "Everyone can view role categories" ON role_categories
  FOR SELECT USING (true);

-- Only Chapter Chairman and Secretary can manage roles
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