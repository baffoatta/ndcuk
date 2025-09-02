from typing import List, Optional, Dict, Any
from supabase import Client
from app.core.database import supabase_client
from app.core.exceptions import NotFoundException, ValidationException, AuthorizationException
from app.models.branch import (
    BranchCreate, BranchUpdate, BranchResponse, MembershipCreate,
    MembershipUpdate, MembershipResponse, BranchMembersResponse, BranchStatus
)
import logging

logger = logging.getLogger(__name__)

class BranchService:
    def __init__(self):
        self.client: Client = supabase_client.get_client()
    
    async def list_branches(
        self, 
        chapter_id: Optional[str] = None,
        status: Optional[BranchStatus] = None
    ) -> List[BranchResponse]:
        """List branches with optional filtering"""
        try:
            query = self.client.table("branches").select(
                """
                *,
                chapters (name),
                created_by_profile:user_profiles!created_by (full_name)
                """
            ).order("name")
            
            if chapter_id:
                query = query.eq("chapter_id", chapter_id)
            
            if status:
                query = query.eq("status", status.value)
            else:
                query = query.eq("status", "active")  # Default to active branches
            
            response = query.execute()
            
            branches = []
            for branch_data in response.data:
                # Get member count
                member_count_response = self.client.table("memberships").select(
                    "id", count="exact"
                ).eq("branch_id", branch_data["id"]).eq("status", "active").execute()
                
                member_count = member_count_response.count or 0
                
                branches.append(BranchResponse(
                    id=branch_data["id"],
                    name=branch_data["name"],
                    location=branch_data["location"],
                    description=branch_data.get("description"),
                    min_members=branch_data.get("min_members", 20),
                    chapter_id=branch_data["chapter_id"],
                    chapter_name=branch_data.get("chapters", {}).get("name"),
                    status=branch_data["status"],
                    member_count=member_count,
                    created_by=branch_data.get("created_by"),
                    created_by_name=branch_data.get("created_by_profile", {}).get("full_name"),
                    created_at=branch_data["created_at"],
                    updated_at=branch_data["updated_at"]
                ))
            
            return branches
            
        except Exception as e:
            logger.error(f"List branches error: {e}")
            raise ValidationException("Failed to fetch branches")
    
    async def get_branch(self, branch_id: str) -> Optional[BranchResponse]:
        """Get branch by ID"""
        try:
            response = self.client.table("branches").select(
                """
                *,
                chapters (name),
                created_by_profile:user_profiles!created_by (full_name)
                """
            ).eq("id", branch_id).execute()
            
            if not response.data:
                return None
            
            branch_data = response.data[0]
            
            # Get member count
            member_count_response = self.client.table("memberships").select(
                "id", count="exact"
            ).eq("branch_id", branch_id).eq("status", "active").execute()
            
            member_count = member_count_response.count or 0
            
            return BranchResponse(
                id=branch_data["id"],
                name=branch_data["name"],
                location=branch_data["location"],
                description=branch_data.get("description"),
                min_members=branch_data.get("min_members", 20),
                chapter_id=branch_data["chapter_id"],
                chapter_name=branch_data.get("chapters", {}).get("name"),
                status=branch_data["status"],
                member_count=member_count,
                created_by=branch_data.get("created_by"),
                created_by_name=branch_data.get("created_by_profile", {}).get("full_name"),
                created_at=branch_data["created_at"],
                updated_at=branch_data["updated_at"]
            )
            
        except Exception as e:
            logger.error(f"Get branch error: {e}")
            return None
    
    async def create_branch(self, branch_data: BranchCreate, creator_id: str) -> BranchResponse:
        """Create new branch"""
        try:
            # Check if branch name already exists in chapter
            existing_response = self.client.table("branches").select("id").eq(
                "chapter_id", branch_data.chapter_id
            ).eq("name", branch_data.name).execute()
            
            if existing_response.data:
                raise ValidationException("Branch name already exists in this chapter")
            
            # Prepare branch data
            branch_dict = branch_data.dict()
            branch_dict["created_by"] = creator_id
            
            response = self.client.table("branches").insert(branch_dict).execute()
            
            if not response.data:
                raise ValidationException("Branch creation failed")
            
            return await self.get_branch(response.data[0]["id"])
            
        except Exception as e:
            logger.error(f"Create branch error: {e}")
            if isinstance(e, ValidationException):
                raise
            raise ValidationException("Branch creation failed")
    
    async def update_branch(
        self, 
        branch_id: str, 
        branch_data: BranchUpdate, 
        updater_id: str
    ) -> BranchResponse:
        """Update branch"""
        try:
            # Check if branch exists
            branch = await self.get_branch(branch_id)
            if not branch:
                raise NotFoundException("Branch not found")
            
            # Prepare update data
            update_dict = branch_data.dict(exclude_none=True)
            if update_dict:
                update_dict["updated_at"] = "now()"
                
                response = self.client.table("branches").update(update_dict).eq("id", branch_id).execute()
                
                if not response.data:
                    raise ValidationException("Branch update failed")
            
            return await self.get_branch(branch_id)
            
        except Exception as e:
            logger.error(f"Update branch error: {e}")
            if isinstance(e, (NotFoundException, ValidationException)):
                raise
            raise ValidationException("Branch update failed")
    
    async def delete_branch(self, branch_id: str, deleter_id: str) -> Dict[str, Any]:
        """Delete branch (soft delete)"""
        try:
            # Check if branch exists
            branch = await self.get_branch(branch_id)
            if not branch:
                raise NotFoundException("Branch not found")
            
            # Check if branch has active members
            member_count_response = self.client.table("memberships").select(
                "id", count="exact"
            ).eq("branch_id", branch_id).eq("status", "active").execute()
            
            if member_count_response.count and member_count_response.count > 0:
                raise ValidationException("Cannot delete branch with active members")
            
            # Soft delete by setting status to inactive
            response = self.client.table("branches").update({
                "status": "inactive",
                "updated_at": "now()"
            }).eq("id", branch_id).execute()
            
            if not response.data:
                raise ValidationException("Branch deletion failed")
            
            return {"message": "Branch deleted successfully"}
            
        except Exception as e:
            logger.error(f"Delete branch error: {e}")
            if isinstance(e, (NotFoundException, ValidationException)):
                raise
            raise ValidationException("Branch deletion failed")
    
    async def get_branch_members(
        self, 
        branch_id: str,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> BranchMembersResponse:
        """Get branch members with pagination"""
        try:
            # Check if branch exists
            branch = await self.get_branch(branch_id)
            if not branch:
                raise NotFoundException("Branch not found")
            
            offset = (page - 1) * size
            
            query = self.client.table("memberships").select(
                """
                *,
                user_profiles (full_name),
                approved_by_profile:user_profiles!approved_by (full_name)
                """,
                count="exact"
            ).eq("branch_id", branch_id)
            
            if status:
                query = query.eq("status", status)
            
            query = query.range(offset, offset + size - 1).order("joined_date", desc=True)
            
            response = query.execute()
            
            members = []
            for membership_data in response.data:
                # Get user email (would need to join with auth.users in real implementation)
                members.append(MembershipResponse(
                    id=membership_data["id"],
                    user_id=membership_data["user_id"],
                    branch_id=membership_data["branch_id"],
                    status=membership_data["status"],
                    joined_date=membership_data["joined_date"],
                    approved_by=membership_data.get("approved_by"),
                    approved_by_name=membership_data.get("approved_by_profile", {}).get("full_name"),
                    approved_at=membership_data.get("approved_at"),
                    card_issued=membership_data["card_issued"],
                    card_issued_at=membership_data.get("card_issued_at"),
                    user_name=membership_data.get("user_profiles", {}).get("full_name"),
                    user_email="",  # Would need to fetch from auth.users
                    branch_name=branch.name,
                    created_at=membership_data["created_at"],
                    updated_at=membership_data["updated_at"]
                ))
            
            return BranchMembersResponse(
                members=members,
                total=response.count or 0,
                branch_id=branch_id,
                branch_name=branch.name
            )
            
        except Exception as e:
            logger.error(f"Get branch members error: {e}")
            if isinstance(e, NotFoundException):
                raise
            raise ValidationException("Failed to fetch branch members")
    
    async def add_member_to_branch(
        self, 
        membership_data: MembershipCreate,
        adder_id: str
    ) -> MembershipResponse:
        """Add member to branch"""
        try:
            # Check if membership already exists
            existing_response = self.client.table("memberships").select("id").eq(
                "user_id", membership_data.user_id
            ).eq("branch_id", membership_data.branch_id).execute()
            
            if existing_response.data:
                raise ValidationException("User is already a member of this branch")
            
            # Create membership
            membership_dict = membership_data.dict()
            membership_dict["status"] = "pending"  # New members start as pending
            
            response = self.client.table("memberships").insert(membership_dict).execute()
            
            if not response.data:
                raise ValidationException("Membership creation failed")
            
            return await self.get_membership(response.data[0]["id"])
            
        except Exception as e:
            logger.error(f"Add member to branch error: {e}")
            if isinstance(e, ValidationException):
                raise
            raise ValidationException("Membership creation failed")
    
    async def update_membership(
        self, 
        membership_id: str,
        membership_data: MembershipUpdate,
        updater_id: str
    ) -> MembershipResponse:
        """Update membership status"""
        try:
            # Get existing membership
            membership = await self.get_membership(membership_id)
            if not membership:
                raise NotFoundException("Membership not found")
            
            # Prepare update data
            update_dict = membership_data.dict(exclude_none=True)
            if update_dict:
                update_dict["updated_at"] = "now()"
                
                # If approving membership, set approver and approval date
                if membership_data.status == "active" and membership.status == "pending":
                    update_dict["approved_by"] = updater_id
                    update_dict["approved_at"] = "now()"
                
                response = self.client.table("memberships").update(update_dict).eq("id", membership_id).execute()
                
                if not response.data:
                    raise ValidationException("Membership update failed")
            
            return await self.get_membership(membership_id)
            
        except Exception as e:
            logger.error(f"Update membership error: {e}")
            if isinstance(e, (NotFoundException, ValidationException)):
                raise
            raise ValidationException("Membership update failed")
    
    async def get_membership(self, membership_id: str) -> Optional[MembershipResponse]:
        """Get membership by ID"""
        try:
            response = self.client.table("memberships").select(
                """
                *,
                user_profiles (full_name),
                branches (name),
                approved_by_profile:user_profiles!approved_by (full_name)
                """
            ).eq("id", membership_id).execute()
            
            if not response.data:
                return None
            
            membership_data = response.data[0]
            
            return MembershipResponse(
                id=membership_data["id"],
                user_id=membership_data["user_id"],
                branch_id=membership_data["branch_id"],
                status=membership_data["status"],
                joined_date=membership_data["joined_date"],
                approved_by=membership_data.get("approved_by"),
                approved_by_name=membership_data.get("approved_by_profile", {}).get("full_name"),
                approved_at=membership_data.get("approved_at"),
                card_issued=membership_data["card_issued"],
                card_issued_at=membership_data.get("card_issued_at"),
                user_name=membership_data.get("user_profiles", {}).get("full_name"),
                user_email="",  # Would need to fetch from auth.users
                branch_name=membership_data.get("branches", {}).get("name"),
                created_at=membership_data["created_at"],
                updated_at=membership_data["updated_at"]
            )
            
        except Exception as e:
            logger.error(f"Get membership error: {e}")
            return None

# Global instance
branch_service = BranchService()