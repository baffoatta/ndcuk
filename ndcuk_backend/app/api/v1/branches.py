from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from app.models.branch import (
    BranchCreate, BranchUpdate, BranchResponse, BranchListResponse,
    MembershipCreate, MembershipUpdate, MembershipResponse, BranchMembersResponse,
    BranchStatus
)
from app.services.branch_service import branch_service
from app.api.dependencies import (
    get_current_user, get_current_active_user, require_chapter_leadership,
    require_branch_management, require_any_leadership, get_user_branch_access
)
from app.core.exceptions import NotFoundException, ValidationException, AuthorizationException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/branches", tags=["Branch Management"])

@router.get("/public", response_model=List[Dict[str, Any]])
async def list_branches_public():
    """List active branches for registration (public endpoint)"""
    try:
        # Use service key client to bypass RLS for public access
        from app.core.database import supabase_client
        client = supabase_client.get_client(use_service_key=True)
        
        response = client.table("branches").select(
            "id, name, location, description"
        ).eq("status", "active").execute()
        
        return response.data if response.data else []
    except Exception as e:
        logger.error(f"List public branches error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch branches")

@router.get("/", response_model=BranchListResponse)
async def list_branches(
    chapter_id: Optional[str] = Query(None, description="Filter by chapter ID"),
    status: Optional[BranchStatus] = Query(None, description="Filter by status"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """List branches with optional filtering"""
    try:
        branches = await branch_service.list_branches(chapter_id=chapter_id, status=status)
        
        return BranchListResponse(
            branches=branches,
            total=len(branches)
        )
    except Exception as e:
        logger.error(f"List branches endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch branches")

@router.post("/", response_model=BranchResponse)
async def create_branch(
    branch_data: BranchCreate,
    current_user: Dict[str, Any] = Depends(require_chapter_leadership)
):
    """Create new branch (requires chapter leadership)"""
    try:
        branch = await branch_service.create_branch(branch_data, current_user["id"])
        return branch
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Create branch endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Branch creation failed")

@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch(
    branch_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get branch details by ID"""
    try:
        branch = await branch_service.get_branch(branch_id)
        if not branch:
            raise NotFoundException("Branch not found")
        return branch
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Get branch endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch branch")

@router.put("/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: str,
    branch_data: BranchUpdate,
    current_user: Dict[str, Any] = Depends(require_any_leadership),
    accessible_branches: list = Depends(get_user_branch_access)
):
    """Update branch (requires leadership role)"""
    try:
        # Check if user has access to this branch
        if accessible_branches != ["all"] and branch_id not in accessible_branches:
            raise AuthorizationException("No access to this branch")
        
        branch = await branch_service.update_branch(branch_id, branch_data, current_user["id"])
        return branch
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Update branch endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Branch update failed")

@router.delete("/{branch_id}", response_model=Dict[str, Any])
async def delete_branch(
    branch_id: str,
    current_user: Dict[str, Any] = Depends(require_chapter_leadership)
):
    """Delete branch (requires chapter leadership)"""
    try:
        result = await branch_service.delete_branch(branch_id, current_user["id"])
        return result
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Delete branch endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Branch deletion failed")

@router.get("/{branch_id}/members", response_model=BranchMembersResponse)
async def get_branch_members(
    branch_id: str,
    status: Optional[str] = Query(None, description="Filter by membership status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    current_user: Dict[str, Any] = Depends(require_any_leadership),
    accessible_branches: list = Depends(get_user_branch_access)
):
    """Get branch members (requires leadership role)"""
    try:
        # Check if user has access to this branch
        if accessible_branches != ["all"] and branch_id not in accessible_branches:
            raise AuthorizationException("No access to this branch")
        
        members = await branch_service.get_branch_members(
            branch_id=branch_id,
            status=status,
            page=page,
            size=size
        )
        return members
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Get branch members endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch branch members")

@router.post("/{branch_id}/members", response_model=MembershipResponse)
async def add_member_to_branch(
    branch_id: str,
    user_id: str = Query(..., description="User ID to add to branch"),
    current_user: Dict[str, Any] = Depends(require_any_leadership),
    accessible_branches: list = Depends(get_user_branch_access)
):
    """Add member to branch (requires leadership role)"""
    try:
        # Check if user has access to this branch
        if accessible_branches != ["all"] and branch_id not in accessible_branches:
            raise AuthorizationException("No access to this branch")
        
        membership_data = MembershipCreate(user_id=user_id, branch_id=branch_id)
        membership = await branch_service.add_member_to_branch(membership_data, current_user["id"])
        return membership
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Add member to branch endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to add member to branch")

@router.put("/{branch_id}/members/{user_id}/approve", response_model=MembershipResponse)
async def approve_branch_member(
    branch_id: str,
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_any_leadership),
    accessible_branches: list = Depends(get_user_branch_access)
):
    """Approve branch member (requires leadership role)"""
    try:
        # Check if user has access to this branch
        if accessible_branches != ["all"] and branch_id not in accessible_branches:
            raise AuthorizationException("No access to this branch")
        
        # Find membership
        membership_response = await branch_service.client.table("memberships").select("id").eq(
            "user_id", user_id
        ).eq("branch_id", branch_id).execute()
        
        if not membership_response.data:
            raise NotFoundException("Membership not found")
        
        membership_id = membership_response.data[0]["id"]
        membership_data = MembershipUpdate(status="active")
        membership = await branch_service.update_membership(membership_id, membership_data, current_user["id"])
        return membership
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Approve branch member endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Member approval failed")

@router.put("/memberships/{membership_id}", response_model=MembershipResponse)
async def update_membership(
    membership_id: str,
    membership_data: MembershipUpdate,
    current_user: Dict[str, Any] = Depends(require_any_leadership)
):
    """Update membership status (requires leadership role)"""
    try:
        # Get membership to check branch access
        membership = await branch_service.get_membership(membership_id)
        if not membership:
            raise NotFoundException("Membership not found")
        
        # Check branch access
        accessible_branches = await get_user_branch_access(current_user)
        if accessible_branches != ["all"] and membership.branch_id not in accessible_branches:
            raise AuthorizationException("No access to this membership")
        
        updated_membership = await branch_service.update_membership(membership_id, membership_data, current_user["id"])
        return updated_membership
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Update membership endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Membership update failed")

@router.get("/memberships/{membership_id}", response_model=MembershipResponse)
async def get_membership(
    membership_id: str,
    current_user: Dict[str, Any] = Depends(require_any_leadership)
):
    """Get membership details (requires leadership role)"""
    try:
        membership = await branch_service.get_membership(membership_id)
        if not membership:
            raise NotFoundException("Membership not found")
        
        # Check branch access
        accessible_branches = await get_user_branch_access(current_user)
        if accessible_branches != ["all"] and membership.branch_id not in accessible_branches:
            raise AuthorizationException("No access to this membership")
        
        return membership
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Get membership endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch membership")

@router.get("/my-branches", response_model=List[BranchResponse])
async def get_my_branches(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """Get branches where current user is a member"""
    try:
        # Get user's memberships
        membership_response = await branch_service.client.table("memberships").select(
            "branch_id"
        ).eq("user_id", current_user["id"]).eq("status", "active").execute()
        
        if not membership_response.data:
            return []
        
        branch_ids = [m["branch_id"] for m in membership_response.data]
        
        branches = []
        for branch_id in branch_ids:
            branch = await branch_service.get_branch(branch_id)
            if branch:
                branches.append(branch)
        
        return branches
    except Exception as e:
        logger.error(f"Get my branches endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch branches")

@router.post("/{branch_id}/members/{user_id}/issue-card", response_model=Dict[str, Any])
async def issue_membership_card(
    branch_id: str,
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_any_leadership),
    accessible_branches: list = Depends(get_user_branch_access)
):
    """Issue membership card to approved member"""
    try:
        # Check if user has access to this branch
        if accessible_branches != ["all"] and branch_id not in accessible_branches:
            raise AuthorizationException("No access to this branch")
        
        # Find membership
        membership_response = await branch_service.client.table("memberships").select("id").eq(
            "user_id", user_id
        ).eq("branch_id", branch_id).execute()
        
        if not membership_response.data:
            raise NotFoundException("Membership not found")
        
        membership_id = membership_response.data[0]["id"]
        membership_data = MembershipUpdate(card_issued=True)
        await branch_service.update_membership(membership_id, membership_data, current_user["id"])
        
        return {"message": "Membership card issued successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Issue membership card endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Card issuance failed")