-- Fix the user registration trigger function
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
DROP FUNCTION IF EXISTS handle_new_user();

-- Create improved trigger function
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
DECLARE
  membership_num TEXT;
  user_full_name TEXT;
  user_phone TEXT;
  user_branch_id UUID;
  user_address TEXT;
  user_dob DATE;
BEGIN
  -- Generate membership number
  SELECT generate_membership_number() INTO membership_num;
  
  -- Extract metadata safely
  user_full_name := COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.email);
  user_phone := NEW.raw_user_meta_data->>'phone';
  user_branch_id := NULLIF(NEW.raw_user_meta_data->>'branch_id', '')::UUID;
  user_address := NEW.raw_user_meta_data->>'address';
  
  -- Handle date_of_birth safely
  BEGIN
    user_dob := (NEW.raw_user_meta_data->>'date_of_birth')::DATE;
  EXCEPTION WHEN OTHERS THEN
    user_dob := NULL;
  END;
  
  -- Insert user profile
  INSERT INTO user_profiles (
    id, 
    full_name, 
    phone,
    address,
    date_of_birth,
    membership_number,
    email_verified
  )
  VALUES (
    NEW.id,
    user_full_name,
    user_phone,
    user_address,
    user_dob,
    membership_num,
    NEW.email_confirmed_at IS NOT NULL
  );
  
  -- Create membership if branch_id is provided
  IF user_branch_id IS NOT NULL THEN
    INSERT INTO memberships (user_id, branch_id, status)
    VALUES (NEW.id, user_branch_id, 'pending')
    ON CONFLICT (user_id, branch_id) DO NOTHING;
  END IF;
  
  RETURN NEW;
EXCEPTION WHEN OTHERS THEN
  -- Log error but don't fail the user creation
  RAISE WARNING 'Error in handle_new_user trigger: %', SQLERRM;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Recreate the trigger
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();