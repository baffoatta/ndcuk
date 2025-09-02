-- Disable the problematic trigger that's causing registration failures
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

-- Optional: Also disable the email verification trigger for now
DROP TRIGGER IF EXISTS on_auth_user_confirmed ON auth.users;