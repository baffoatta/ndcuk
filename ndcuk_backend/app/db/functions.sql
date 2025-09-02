-- NDC UK Backend Database Functions
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