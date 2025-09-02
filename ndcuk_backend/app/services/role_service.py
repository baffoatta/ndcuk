from typing import List, Optional, Dict, Any
from supabase import Client
from app.core.database import supabase_client
from app.core.exceptions import NotFoundException, ValidationException, AuthorizationException
from app.models.role import (
    RoleResponse, RoleCategoryResponse, ExecutiveAssignmentCreate, 
    ExecutiveAssignmentResponse, ExecutiveAssignmentUpdate
)
import logging

logger = logging.getLogger(__name__)

class RoleService:
    def __init__(self):
        self.client: Client = supabase_client.get_client()
    
    async def list_roles(self, category_id: Optional[str] = None, scope_type: Optional[str] = None) -> List[RoleResponse]:
        """List all active roles with optional filtering"""
        try:
            query = self.client.table("roles").select(
                """
                *,
                role_categories (
                    name
                )
                """
            ).eq("is_active", True).order("name")
            
            if category_id:
                query = query.eq("category_id", category_id)
            
            if scope_type:
                query = query.eq("scope_type", scope_type)
            
            response = query.execute()
            
            roles = []
            for role_data in response.data:
                category_name = None
                if role_data.get("role_categories"):
                    category_name = role_data["role_categories"]["name"]
                
                roles.append(RoleResponse(
                    id=role_data["id"],
                    name=role_data["name"],
                    scope_type=role_data["scope_type"],
                    category_id=role_data.get("category_id"),
                    category_name=category_name,
                    description=role_data.get("description"),
                    permissions=role_data.get("permissions", {}),
                    is_active=role_data["is_active"],
                    created_at=role_data["created_at"],
                    updated_at=role_data["updated_at"]
                ))
            
            return roles
            
        except Exception as e:
            logger.error(f"List roles error: {e}")
            raise ValidationException("Failed to fetch roles")
    
    async def get_role(self, role_id: str) -> Optional[RoleResponse]:
        """Get role by ID"""
        try:
            response = self.client.table("roles").select(
                """
                *,
                role_categories (
                    name
                )
                """
            ).eq("id", role_id).execute()
            
            if not response.data:
                return None
            
            role_data = response.data[0]
            category_name = None
            if role_data.get("role_categories"):
                category_name = role_data["role_categories"]["name"]
            
            return RoleResponse(
                id=role_data["id"],
                name=role_data["name"],
                scope_type=role_data["scope_type"],
                category_id=role_data.get("category_id"),
                category_name=category_name,
                description=role_data.get("description"),
                permissions=role_data.get("permissions", {}),
                is_active=role_data["is_active"],
                created_at=role_data["created_at"],
                updated_at=role_data["updated_at"]
            )
            
        except Exception as e:
            logger.error(f"Get role error: {e}")
            return None
    
    async def list_role_categories(self) -> List[RoleCategoryResponse]:
        """List all role categories"""
        try:
            response = self.client.table("role_categories").select("*").order("sort_order").execute()
            
            categories = []
            for category_data in response.data:
                categories.append(RoleCategoryResponse(
                    id=category_data["id"],
                    name=category_data["name"],
                    description=category_data.get("description"),
                    sort_order=category_data["sort_order"],
                    created_at=category_data["created_at"]
                ))
            
            return categories
            
        except Exception as e:
            logger.error(f"List role categories error: {e}")
            raise ValidationException("Failed to fetch role categories")
    
    async def assign_role(
        self, 
        assignment_data: ExecutiveAssignmentCreate, 
        assigner_id: str
    ) -> ExecutiveAssignmentResponse:
        """Assign role to user"""
        try:
            # Validate role assignment
            can_assign = await self._validate_role_assignment(
                assignment_data.user_id,
                assignment_data.role_id,
                assignment_data.chapter_id,
                assignment_data.branch_id,
                assigner_id
            )
            
            if not can_assign:
                raise AuthorizationException("Not authorized to assign this role")
            
            # Check if role already assigned and active
            existing_response = self.client.table("executive_assignments").select("id").eq(
                "user_id", assignment_data.user_id
            ).eq("role_id", assignment_data.role_id).eq("is_active", True).execute()
            
            if existing_response.data:
                raise ValidationException("User already has this role assigned")
            
            # Create assignment
            assignment_dict = assignment_data.dict(exclude_none=True)
            assignment_dict["appointed_by"] = assigner_id
            
            response = self.client.table("executive_assignments").insert(assignment_dict).execute()
            
            if not response.data:
                raise ValidationException("Role assignment failed")
            
            return await self.get_assignment(response.data[0]["id"])
            
        except Exception as e:
            logger.error(f"Assign role error: {e}")
            if isinstance(e, (ValidationException, AuthorizationException)):
                raise
            raise ValidationException("Role assignment failed")
    
    async def update_assignment(
        self, 
        assignment_id: str, 
        update_data: ExecutiveAssignmentUpdate,
        updater_id: str
    ) -> ExecutiveAssignmentResponse:
        """Update role assignment"""
        try:
            # Get existing assignment
            assignment = await self.get_assignment(assignment_id)
            if not assignment:
                raise NotFoundException("Assignment not found")
            
            # Validate permission to update
            can_update = await self._validate_assignment_update(assignment_id, updater_id)
            if not can_update:
                raise AuthorizationException("Not authorized to update this assignment")
            
            update_dict = update_data.dict(exclude_none=True)
            update_dict["updated_at"] = "now()"
            
            response = self.client.table("executive_assignments").update(update_dict).eq("id", assignment_id).execute()
            
            if not response.data:
                raise ValidationException("Assignment update failed")
            
            return await self.get_assignment(assignment_id)
            
        except Exception as e:
            logger.error(f"Update assignment error: {e}")
            if isinstance(e, (NotFoundException, ValidationException, AuthorizationException)):
                raise
            raise ValidationException("Assignment update failed")
    
    async def remove_assignment(self, assignment_id: str, remover_id: str) -> Dict[str, Any]:
        """Remove role assignment"""
        try:
            # Validate permission to remove
            can_remove = await self._validate_assignment_update(assignment_id, remover_id)
            if not can_remove:
                raise AuthorizationException("Not authorized to remove this assignment")
            
            # Soft delete by setting is_active to false
            response = self.client.table("executive_assignments").update({
                "is_active": False,
                "end_date": "now()",
                "updated_at": "now()"
            }).eq("id", assignment_id).execute()
            
            if not response.data:
                raise NotFoundException("Assignment not found")
            
            return {"message": "Role assignment removed successfully"}
            
        except Exception as e:
            logger.error(f"Remove assignment error: {e}")
            if isinstance(e, (NotFoundException, AuthorizationException)):
                raise
            raise ValidationException("Assignment removal failed")
    
    async def get_assignment(self, assignment_id: str) -> Optional[ExecutiveAssignmentResponse]:
        """Get assignment by ID"""
        try:
            response = self.client.table("executive_assignments").select(
                """
                *,
                user_profiles (full_name),
                roles (name),
                chapters (name),
                branches (name),
                appointed_by_profile:user_profiles!appointed_by (full_name)
                """
            ).eq("id", assignment_id).execute()
            
            if not response.data:
                return None
            
            assignment_data = response.data[0]
            
            return ExecutiveAssignmentResponse(
                id=assignment_data["id"],
                user_id=assignment_data["user_id"],
                user_name=assignment_data.get("user_profiles", {}).get("full_name"),
                role_id=assignment_data["role_id"],
                role_name=assignment_data.get("roles", {}).get("name"),
                chapter_id=assignment_data.get("chapter_id"),
                chapter_name=assignment_data.get("chapters", {}).get("name"),
                branch_id=assignment_data.get("branch_id"),
                branch_name=assignment_data.get("branches", {}).get("name"),
                start_date=assignment_data["start_date"],
                end_date=assignment_data.get("end_date"),
                is_active=assignment_data["is_active"],
                appointed_by=assignment_data.get("appointed_by"),
                appointed_by_name=assignment_data.get("appointed_by_profile", {}).get("full_name"),
                notes=assignment_data.get("notes"),
                created_at=assignment_data["created_at"],
                updated_at=assignment_data["updated_at"]
            )
            
        except Exception as e:
            logger.error(f"Get assignment error: {e}")
            return None
    
    async def list_user_assignments(self, user_id: str, active_only: bool = True) -> List[ExecutiveAssignmentResponse]:
        """List user's role assignments"""
        try:
            query = self.client.table("executive_assignments").select(
                """
                *,
                roles (name),
                chapters (name),
                branches (name)
                """
            ).eq("user_id", user_id)
            
            if active_only:
                query = query.eq("is_active", True)
            
            response = query.execute()
            
            assignments = []
            for assignment_data in response.data:
                assignments.append(ExecutiveAssignmentResponse(
                    id=assignment_data["id"],
                    user_id=assignment_data["user_id"],
                    role_id=assignment_data["role_id"],
                    role_name=assignment_data.get("roles", {}).get("name"),
                    chapter_id=assignment_data.get("chapter_id"),
                    chapter_name=assignment_data.get("chapters", {}).get("name"),
                    branch_id=assignment_data.get("branch_id"),
                    branch_name=assignment_data.get("branches", {}).get("name"),
                    start_date=assignment_data["start_date"],
                    end_date=assignment_data.get("end_date"),
                    is_active=assignment_data["is_active"],
                    appointed_by=assignment_data.get("appointed_by"),
                    notes=assignment_data.get("notes"),
                    created_at=assignment_data["created_at"],
                    updated_at=assignment_data["updated_at"]
                ))
            
            return assignments
            
        except Exception as e:
            logger.error(f"List user assignments error: {e}")
            return []
    
    async def _validate_role_assignment(
        self, 
        user_id: str, 
        role_id: str, 
        chapter_id: Optional[str], 
        branch_id: Optional[str],
        assigner_id: str
    ) -> bool:
        """Validate if assigner can assign role to user"""
        try:
            # Call database function
            response = self.client.rpc("can_assign_role", {
                "assigner_user_id": assigner_id,
                "target_user_id": user_id,
                "role_id": role_id,
                "target_chapter_id": chapter_id,
                "target_branch_id": branch_id
            }).execute()
            
            return response.data if response.data is not None else False
            
        except Exception as e:
            logger.error(f"Validate role assignment error: {e}")
            return False
    
    async def _validate_assignment_update(self, assignment_id: str, updater_id: str) -> bool:
        """Validate if user can update assignment"""
        try:
            # Get assignment details
            assignment = await self.get_assignment(assignment_id)
            if not assignment:
                return False
            
            # Check if updater has permission (simplified logic)
            updater_roles = self.client.table("executive_assignments").select(
                "roles (name)"
            ).eq("user_id", updater_id).eq("is_active", True).execute()
            
            for role_assignment in updater_roles.data:
                role_name = role_assignment.get("roles", {}).get("name")
                if role_name in ["Chairman", "Secretary"]:
                    return True
                if role_name == "Branch Chairman" and assignment.branch_id:
                    # Check if same branch
                    branch_chairman_assignment = self.client.table("executive_assignments").select("branch_id").eq(
                        "user_id", updater_id
                    ).eq("is_active", True).execute()
                    
                    for ba in branch_chairman_assignment.data:
                        if ba["branch_id"] == assignment.branch_id:
                            return True
            
            return False
            
        except Exception as e:
            logger.error(f"Validate assignment update error: {e}")
            return False

# Global instance
role_service = RoleService()