from typing import Optional, Dict, Any
from supabase import Client
from app.core.database import supabase_client
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.exceptions import AuthenticationException, ValidationException
from app.models.auth import UserRegister, UserLogin, SocialLogin, Token
from app.models.user import UserResponse
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.client: Client = supabase_client.get_client()
    
    async def _generate_membership_number(self) -> str:
        """Generate unique membership number"""
        try:
            # Get current year
            from datetime import datetime
            current_year = datetime.now().year
            
            # Count existing memberships to get next number
            count_response = self.client.table("user_profiles").select("id", count="exact").execute()
            next_number = (count_response.count or 0) + 1
            
            # Format: NDC-YYYY-XXXX (e.g., NDC-2024-0001)
            return f"NDC-{current_year}-{next_number:04d}"
            
        except Exception as e:
            logger.error(f"Membership number generation error: {e}")
            # Fallback to timestamp-based number
            import time
            return f"NDC-{datetime.now().year}-{int(time.time()) % 10000:04d}"
    
    async def register_user(self, user_data: UserRegister) -> Dict[str, Any]:
        """Register a new user with email and password"""
        try:
            # Find branch by name
            branch_response = self.client.table("branches").select("id").eq(
                "name", user_data.branch_name
            ).eq("status", "active").execute()
            
            if not branch_response.data:
                raise ValidationException(f'Branch "{user_data.branch_name}" is not available or not active')
            
            branch_id = branch_response.data[0]["id"]
            
            # Register user in Supabase Auth (without metadata to avoid trigger issues)
            auth_response = self.client.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password
            })
            
            if auth_response.user is None:
                raise ValidationException("Registration failed")
            
            # Generate membership number
            membership_number = await self._generate_membership_number()
            
            # Create user profile manually with all new fields
            profile_data = {
                "id": auth_response.user.id,
                "full_name": user_data.full_name,
                "address": user_data.address,
                "date_of_birth": user_data.date_of_birth.isoformat(),
                "gender": user_data.gender,
                "occupation": user_data.occupation,
                "qualification": user_data.qualification,
                "membership_number": membership_number,
                "email_verified": auth_response.user.email_confirmed_at is not None,
                "status": "not_approved"
            }
            
            # Handle profile picture if provided
            if user_data.profile_picture:
                profile_data["avatar_url"] = user_data.profile_picture
            
            profile_response = self.client.table("user_profiles").insert(profile_data).execute()
            
            if not profile_response.data:
                logger.error(f"Profile creation failed for user {auth_response.user.id}")
                # Try to delete the auth user if profile creation fails
                try:
                    self.client.auth.admin.delete_user(auth_response.user.id)
                except:
                    pass
                raise ValidationException("Failed to create user profile")
            
            # Create membership record using the found branch_id
            membership_data = {
                "user_id": auth_response.user.id,
                "branch_id": branch_id,
                "status": "pending"
            }
            
            membership_response = self.client.table("memberships").insert(membership_data).execute()
            
            if not membership_response.data:
                logger.warning(f"Membership creation failed for user {auth_response.user.id}")
            
            return {
                "message": "Registration successful. Please check your email to verify your account.",
                "user_id": auth_response.user.id,
                "membership_number": membership_number,
                "branch_name": user_data.branch_name,
                "email_confirmed": auth_response.user.email_confirmed_at is not None
            }
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            logger.error(f"Registration error type: {type(e)}")
            if hasattr(e, 'details'):
                logger.error(f"Registration error details: {e.details}")
            if "email" in str(e).lower():
                raise ValidationException("Email already registered")
            raise ValidationException(f"Database error saving new user")
    
    async def login_user(self, login_data: UserLogin) -> Token:
        """Login user with email and password"""
        try:
            # Authenticate with Supabase
            auth_response = self.client.auth.sign_in_with_password({
                "email": login_data.email,
                "password": login_data.password
            })
            
            if auth_response.user is None:
                raise AuthenticationException("Invalid credentials")
            
            # Get user profile with role information
            user_profile = await self.get_user_with_roles(auth_response.user.id)
            
            if not user_profile:
                raise AuthenticationException("User profile not found")
            
            # Create tokens
            access_token = create_access_token(auth_response.user.id)
            refresh_token = create_refresh_token(auth_response.user.id)
            
            return Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer"
            )
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            if "Invalid credentials" in str(e):
                raise AuthenticationException("Invalid email or password")
            raise AuthenticationException("Login failed")
    
    async def social_login(self, social_data: SocialLogin) -> Token:
        """Handle social login (Google/Apple)"""
        try:
            # This would integrate with Supabase social auth
            # For now, return basic implementation
            raise ValidationException("Social login not yet implemented")
            
        except Exception as e:
            logger.error(f"Social login error: {e}")
            raise AuthenticationException("Social login failed")
    
    async def refresh_access_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token"""
        try:
            user_id = verify_token(refresh_token)
            if not user_id:
                raise AuthenticationException("Invalid refresh token")
            
            # Create new tokens
            new_access_token = create_access_token(user_id)
            new_refresh_token = create_refresh_token(user_id)
            
            return Token(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                token_type="bearer"
            )
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            raise AuthenticationException("Token refresh failed")
    
    async def verify_email(self, token: str) -> Dict[str, Any]:
        """Verify user email address"""
        try:
            # Verify with Supabase
            verify_response = self.client.auth.verify_otp({
                "token": token,
                "type": "email"
            })
            
            if verify_response.user is None:
                raise ValidationException("Invalid verification token")
            
            return {
                "message": "Email verified successfully",
                "user_id": verify_response.user.id
            }
            
        except Exception as e:
            logger.error(f"Email verification error: {e}")
            raise ValidationException("Email verification failed")
    
    async def request_password_reset(self, email: str) -> Dict[str, Any]:
        """Request password reset"""
        try:
            reset_response = self.client.auth.reset_password_email(email)
            
            return {
                "message": "If an account with this email exists, a password reset link has been sent."
            }
            
        except Exception as e:
            logger.error(f"Password reset request error: {e}")
            return {
                "message": "If an account with this email exists, a password reset link has been sent."
            }
    
    async def reset_password(self, token: str, new_password: str) -> Dict[str, Any]:
        """Reset password with token"""
        try:
            # This would handle password reset with Supabase
            # Implementation depends on frontend flow
            raise ValidationException("Password reset not yet implemented")
            
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            raise ValidationException("Password reset failed")
    
    async def get_user_with_roles(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile with role information"""
        try:
            # Get user profile
            profile_response = self.client.table("user_profiles").select(
                """
                *,
                memberships (
                    id,
                    status,
                    branch_id,
                    branches (
                        id,
                        name,
                        location
                    )
                ),
                executive_assignments (
                    id,
                    role_id,
                    chapter_id,
                    branch_id,
                    is_active,
                    roles (
                        id,
                        name,
                        scope_type,
                        permissions
                    )
                )
                """
            ).eq("id", user_id).execute()
            
            if not profile_response.data:
                return None
                
            return profile_response.data[0]
            
        except Exception as e:
            logger.error(f"Get user with roles error: {e}")
            return None
    
    async def logout_user(self, access_token: str) -> Dict[str, Any]:
        """Logout user"""
        try:
            # In a real implementation, you might want to blacklist the token
            # For now, just return success message
            return {"message": "Logged out successfully"}
            
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return {"message": "Logged out successfully"}

# Global instance
auth_service = AuthService()