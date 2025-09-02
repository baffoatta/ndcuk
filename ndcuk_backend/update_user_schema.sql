-- Update user_profiles table to include new fields for registration
ALTER TABLE user_profiles 
ADD COLUMN IF NOT EXISTS gender text CHECK (gender IN ('Male', 'Female')),
ADD COLUMN IF NOT EXISTS occupation text,
ADD COLUMN IF NOT EXISTS qualification text;

-- Make address and date_of_birth required (non-nullable)
-- Note: Only do this if you're sure existing records have these fields populated
-- ALTER TABLE user_profiles ALTER COLUMN address SET NOT NULL;
-- ALTER TABLE user_profiles ALTER COLUMN date_of_birth SET NOT NULL;

-- Add constraint for gender if needed
-- ALTER TABLE user_profiles ADD CONSTRAINT check_gender CHECK (gender IN ('Male', 'Female'));

-- Create index on commonly searched fields
CREATE INDEX IF NOT EXISTS idx_user_profiles_gender ON user_profiles(gender);
CREATE INDEX IF NOT EXISTS idx_user_profiles_occupation ON user_profiles(occupation);

-- Update branches to include all the new branch names
-- First, let's update existing branches or create new ones
DO $$
DECLARE
    chapter_uuid uuid;
    branch_names text[] := ARRAY[
        'Leicester Branch', 'Leeds Branch', 'Northampton Branch', 'Coventry Branch',
        'Oxford Branch', 'Bedford Branch', 'Swindon Branch', 'Kent Branch',
        'Luton Branch', 'Cambridge Branch', 'West London Branch', 'Bristol Branch',
        'Southampton Branch', 'North London Branch', 'South London Branch', 
        'East London Branch', 'Milton Keynes Branch', 'Birmingham Branch',
        'Telford Branch', 'Glasgow Branch', 'Manchester Branch', 'Liverpool Branch',
        'Sheffield Branch', 'Hull Branch', 'Aldershot', 'Stoke-on-Trent',
        'Wiltshire', 'Reading', 'Walsall', 'Salisbury and Tidworth',
        'Chester', 'Wolverhampton', 'Edinburgh', 'Cardiff', 'Nottingham'
    ];
    branch_name text;
    branch_location text;
BEGIN
    -- Get the chapter ID
    SELECT id INTO chapter_uuid FROM chapters WHERE name = 'NDC UK & Ireland' LIMIT 1;
    
    IF chapter_uuid IS NULL THEN
        RAISE EXCEPTION 'Chapter "NDC UK & Ireland" not found. Please run the complete database setup first.';
    END IF;
    
    -- Insert all branches
    FOREACH branch_name IN ARRAY branch_names
    LOOP
        -- Extract location from branch name (remove " Branch" suffix if present)
        branch_location := CASE 
            WHEN branch_name LIKE '% Branch' THEN 
                REPLACE(branch_name, ' Branch', '')
            ELSE 
                branch_name
        END;
        
        -- Insert branch if not exists
        INSERT INTO branches (chapter_id, name, location, description, status)
        VALUES (
            chapter_uuid, 
            branch_name, 
            branch_location,
            branch_name || ' - ' || branch_location,
            'active'
        )
        ON CONFLICT (chapter_id, name) DO UPDATE SET
            status = 'active',
            updated_at = NOW();
    END LOOP;
    
    RAISE NOTICE 'Successfully updated % branches', array_length(branch_names, 1);
END
$$;