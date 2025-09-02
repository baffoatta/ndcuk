from typing import Optional, List, Dict, Any
from supabase import Client
from app.core.database import supabase_client
from app.core.exceptions import NotFoundException, ValidationException, AuthorizationException
from app.models.user import UserUpdate, UserResponse, UserStatusUpdate, UserStatus
import logging

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self):
        self.client: Client = supabase_client.get_client()
    
    async def get_user_profile(self, user_id: str) -> Optional[UserResponse]:
        """Get user profile by ID"""
        try:
            response = self.client.table("user_profiles").select(
                """
                *,
                memberships (
                    branch_id,
                    status,
                    branches (name, location)
                )
                """
            ).eq("id", user_id).execute()
            
            if not response.data:
                return None
            
            user_data = response.data[0]
            
            # Get user email from auth.users
            auth_response = self.client.table("auth.users").select("email").eq("id", user_id).execute()
            email = auth_response.data[0]["email"] if auth_response.data else ""
            
            return UserResponse(
                id=user_data["id"],
                email=email,
                full_name=user_data["full_name"],
                phone=user_data.get("phone"),
                address=user_data.get("address"),
                date_of_birth=user_data.get("date_of_birth"),
                membership_number=user_data.get("membership_number"),
                status=user_data["status"],
                email_verified=user_data["email_verified"],
                avatar_url=user_data.get("avatar_url"),
                created_at=user_data["created_at"],
                updated_at=user_data["updated_at"]
            )
            
        except Exception as e:
            logger.error(f"Get user profile error: {e}")
            raise NotFoundException("User not found")
    
    async def update_user_profile(self, user_id: str, user_data: UserUpdate) -> UserResponse:
        """Update user profile"""
        try:
            # Prepare update data
            update_data = {}
            if user_data.full_name is not None:
                update_data["full_name"] = user_data.full_name
            if user_data.phone is not None:
                update_data["phone"] = user_data.phone
            if user_data.address is not None:
                update_data["address"] = user_data.address
            if user_data.date_of_birth is not None:
                update_data["date_of_birth"] = user_data.date_of_birth.isoformat()
            if user_data.avatar_url is not None:
                update_data["avatar_url"] = user_data.avatar_url
            
            if not update_data:
                raise ValidationException("No data provided for update")
            
            update_data["updated_at"] = "now()"
            
            response = self.client.table("user_profiles").update(update_data).eq("id", user_id).execute()
            
            if not response.data:
                raise NotFoundException("User not found")
            
            return await self.get_user_profile(user_id)
            
        except Exception as e:
            logger.error(f"Update user profile error: {e}")
            if isinstance(e, (NotFoundException, ValidationException)):
                raise
            raise ValidationException("Profile update failed")
    
    async def list_users(
        self, 
        page: int = 1, 
        size: int = 20, 
        status: Optional[UserStatus] = None,
        branch_id: Optional[str] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """List users with pagination and filters"""
        try:
            offset = (page - 1) * size
            
            # Build query
            query = self.client.table("user_profiles").select(
                """
                *,
                memberships (
                    branch_id,
                    status,
                    branches (name, location)
                )
                """,
                count="exact"
            )
            
            # Apply filters
            if status:
                query = query.eq("status", status.value)
            
            if branch_id:
                query = query.eq("memberships.branch_id", branch_id)
            
            if search:
                query = query.or_(f"full_name.ilike.%{search}%,membership_number.ilike.%{search}%")
            
            # Apply pagination
            query = query.range(offset, offset + size - 1)
            
            response = query.execute()
            
            users = []
            for user_data in response.data:
                # Get email for each user (if needed)
                users.append(UserResponse(
                    id=user_data["id"],
                    email="",  # Would need to fetch from auth.users
                    full_name=user_data["full_name"],
                    phone=user_data.get("phone"),
                    address=user_data.get("address"),
                    date_of_birth=user_data.get("date_of_birth"),
                    membership_number=user_data.get("membership_number"),
                    status=user_data["status"],
                    email_verified=user_data["email_verified"],
                    avatar_url=user_data.get("avatar_url"),
                    created_at=user_data["created_at"],
                    updated_at=user_data["updated_at"]
                ))
            
            return {
                "users": users,
                "total": response.count or 0,
                "page": page,
                "size": size
            }
            
        except Exception as e:
            logger.error(f"List users error: {e}")
            raise ValidationException("Failed to fetch users")
    
    async def update_user_status(
        self, 
        user_id: str, 
        status_data: UserStatusUpdate, 
        approver_id: str
    ) -> UserResponse:
        """Update user status (approve/suspend/etc)"""
        try:
            # Verify user exists
            user = await self.get_user_profile(user_id)
            if not user:
                raise NotFoundException("User not found")
            
            # Update user status
            update_data = {
                "status": status_data.status.value,
                "updated_at": "now()"
            }
            
            response = self.client.table("user_profiles").update(update_data).eq("id", user_id).execute()
            
            if not response.data:
                raise ValidationException("Status update failed")
            
            # If approving, update membership status
            if status_data.status == UserStatus.APPROVED:
                membership_update = self.client.table("memberships").update({
                    "status": "active",
                    "approved_by": approver_id,
                    "approved_at": "now()"
                }).eq("user_id", user_id).execute()
                
                if not membership_update.data:
                    logger.warning(f"Membership status update failed for user {user_id}")
            
            return await self.get_user_profile(user_id)
            
        except Exception as e:
            logger.error(f"Update user status error: {e}")
            if isinstance(e, (NotFoundException, ValidationException)):
                raise
            raise ValidationException("Status update failed")
    
    async def upload_avatar(self, user_id: str, file_path: str) -> Dict[str, Any]:
        """Upload user avatar"""
        try:
            # This would handle file upload to Supabase Storage
            # For now, just update the avatar_url
            update_data = {
                "avatar_url": file_path,
                "updated_at": "now()"
            }
            
            response = self.client.table("user_profiles").update(update_data).eq("id", user_id).execute()
            
            if not response.data:
                raise NotFoundException("User not found")
            
            return {
                "message": "Avatar uploaded successfully",
                "avatar_url": file_path
            }
            
        except Exception as e:
            logger.error(f"Upload avatar error: {e}")
            raise ValidationException("Avatar upload failed")
    
    async def get_user_permissions(self, user_id: str) -> Dict[str, List[str]]:
        """Get user permissions based on roles"""
        try:
            response = self.client.table("executive_assignments").select(
                """
                roles (
                    name,
                    permissions,
                    scope_type
                )
                """
            ).eq("user_id", user_id).eq("is_active", True).execute()
            
            permissions = {}
            
            for assignment in response.data:
                role = assignment["roles"]
                role_permissions = role.get("permissions", {})
                
                # Merge permissions
                for resource, actions in role_permissions.items():
                    if resource not in permissions:
                        permissions[resource] = []
                    
                    if isinstance(actions, list):
                        permissions[resource].extend(actions)
                    elif actions is True:
                        permissions[resource] = ["all"]
            
            # Remove duplicates
            for resource in permissions:
                permissions[resource] = list(set(permissions[resource]))
            
            return permissions
            
        except Exception as e:
            logger.error(f"Get user permissions error: {e}")
            return {}

# Global instance
user_service = UserService()