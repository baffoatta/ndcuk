from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from typing import Dict, Any, Optional
from app.models.user import UserUpdate, UserResponse, UserListResponse, UserStatusUpdate, UserStatus
from app.services.user_service import user_service
from app.api.dependencies import (
    get_current_user, get_current_active_user, require_any_leadership,
    require_member_management, get_user_branch_access
)
from app.core.exceptions import NotFoundException, ValidationException, AuthorizationException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["User Management"])

@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user's profile"""
    try:
        user_profile = await user_service.get_user_profile(current_user["id"])
        if not user_profile:
            raise NotFoundException("User profile not found")
        return user_profile
    except Exception as e:
        logger.error(f"Get my profile endpoint error: {e}")
        if isinstance(e, NotFoundException):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch profile")

@router.put("/me", response_model=UserResponse)
async def update_my_profile(
    user_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update current user's profile"""
    try:
        updated_user = await user_service.update_user_profile(current_user["id"], user_data)
        return updated_user
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Update my profile endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Profile update failed")

@router.get("/", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    status: Optional[UserStatus] = Query(None, description="Filter by user status"),
    branch_id: Optional[str] = Query(None, description="Filter by branch ID"),
    search: Optional[str] = Query(None, description="Search by name or membership number"),
    current_user: Dict[str, Any] = Depends(require_any_leadership),
    accessible_branches: list = Depends(get_user_branch_access)
):
    """List users with pagination and filtering (requires leadership role)"""
    try:
        # Apply branch access restrictions
        if accessible_branches != ["all"] and branch_id:
            if branch_id not in accessible_branches:
                raise AuthorizationException("No access to this branch")
        elif accessible_branches != ["all"] and not branch_id:
            # If user has limited branch access, default to their branches
            branch_id = accessible_branches[0] if accessible_branches else None
        
        result = await user_service.list_users(
            page=page,
            size=size,
            status=status,
            branch_id=branch_id,
            search=search
        )
        
        return UserListResponse(**result)
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"List users endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch users")

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_any_leadership)
):
    """Get user by ID (requires leadership role)"""
    try:
        user_profile = await user_service.get_user_profile(user_id)
        if not user_profile:
            raise NotFoundException("User not found")
        
        # Check if current user has access to this user's branch
        # This would require additional logic to check branch access
        
        return user_profile
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Get user endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch user")

@router.put("/{user_id}/status", response_model=UserResponse)
async def update_user_status(
    user_id: str,
    status_data: UserStatusUpdate,
    current_user: Dict[str, Any] = Depends(require_member_management)
):
    """Update user status (approve/suspend/etc) - requires member management permission"""
    try:
        updated_user = await user_service.update_user_status(
            user_id=user_id,
            status_data=status_data,
            approver_id=current_user["id"]
        )
        return updated_user
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Update user status endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Status update failed")

@router.put("/{user_id}/approve", response_model=UserResponse)
async def approve_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_member_management)
):
    """Approve user membership - requires member management permission"""
    try:
        status_data = UserStatusUpdate(status=UserStatus.APPROVED)
        updated_user = await user_service.update_user_status(
            user_id=user_id,
            status_data=status_data,
            approver_id=current_user["id"]
        )
        return updated_user
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Approve user endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User approval failed")

@router.post("/{user_id}/avatar", response_model=Dict[str, Any])
async def upload_avatar(
    user_id: str,
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Upload user avatar (users can only upload their own avatar)"""
    try:
        # Check if user can upload avatar for this user_id
        if current_user["id"] != user_id:
            # Check if current user has permission to manage this user
            user_roles = [
                assignment.get("roles", {}).get("name")
                for assignment in current_user.get("executive_assignments", [])
                if assignment.get("is_active")
            ]
            
            if not any(role in ["Chairman", "Secretary"] for role in user_roles):
                raise AuthorizationException("Can only upload own avatar")
        
        # Validate file type and size
        if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
            raise ValidationException("Only JPEG and PNG images are allowed")
        
        # This would handle actual file upload to storage
        # For now, just simulate with filename
        file_path = f"/avatars/{user_id}/{file.filename}"
        
        result = await user_service.upload_avatar(user_id, file_path)
        return result
        
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Upload avatar endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Avatar upload failed")

@router.get("/{user_id}/permissions", response_model=Dict[str, Any])
async def get_user_permissions(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_any_leadership)
):
    """Get user permissions based on their roles"""
    try:
        # Check if requesting own permissions or has leadership role
        if current_user["id"] != user_id:
            user_roles = [
                assignment.get("roles", {}).get("name")
                for assignment in current_user.get("executive_assignments", [])
                if assignment.get("is_active")
            ]
            
            if not any(role in ["Chairman", "Secretary", "Branch Chairman", "Branch Secretary"] for role in user_roles):
                raise AuthorizationException("Not authorized to view user permissions")
        
        permissions = await user_service.get_user_permissions(user_id)
        return {"permissions": permissions}
        
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Get user permissions endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch permissions")