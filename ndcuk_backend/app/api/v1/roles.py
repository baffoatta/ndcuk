from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from app.models.role import (
    RoleResponse, RoleCategoryResponse, ExecutiveAssignmentCreate,
    ExecutiveAssignmentResponse, ExecutiveAssignmentUpdate, RoleAssignmentList,
    RoleScopeType
)
from app.services.role_service import role_service
from app.api.dependencies import (
    get_current_user, get_current_active_user, require_chapter_leadership,
    require_role_management, require_any_leadership
)
from app.core.exceptions import NotFoundException, ValidationException, AuthorizationException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/roles", tags=["Role Management"])

@router.get("/", response_model=List[RoleResponse])
async def list_roles(
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    scope_type: Optional[RoleScopeType] = Query(None, description="Filter by scope type"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """List all active roles with optional filtering"""
    try:
        roles = await role_service.list_roles(category_id=category_id, scope_type=scope_type.value if scope_type else None)
        return roles
    except Exception as e:
        logger.error(f"List roles endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch roles")

@router.get("/categories", response_model=List[RoleCategoryResponse])
async def list_role_categories(current_user: Dict[str, Any] = Depends(get_current_active_user)):
    """List all role categories"""
    try:
        categories = await role_service.list_role_categories()
        return categories
    except Exception as e:
        logger.error(f"List role categories endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch role categories")

@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get role details by ID"""
    try:
        role = await role_service.get_role(role_id)
        if not role:
            raise NotFoundException("Role not found")
        return role
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Get role endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch role")

@router.post("/assignments", response_model=ExecutiveAssignmentResponse)
async def assign_role(
    assignment_data: ExecutiveAssignmentCreate,
    current_user: Dict[str, Any] = Depends(require_any_leadership)
):
    """Assign role to user (requires leadership role)"""
    try:
        assignment = await role_service.assign_role(assignment_data, current_user["id"])
        return assignment
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Assign role endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Role assignment failed")

@router.put("/assignments/{assignment_id}", response_model=ExecutiveAssignmentResponse)
async def update_assignment(
    assignment_id: str,
    update_data: ExecutiveAssignmentUpdate,
    current_user: Dict[str, Any] = Depends(require_any_leadership)
):
    """Update role assignment (requires leadership role)"""
    try:
        assignment = await role_service.update_assignment(assignment_id, update_data, current_user["id"])
        return assignment
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Update assignment endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Assignment update failed")

@router.delete("/assignments/{assignment_id}", response_model=Dict[str, Any])
async def remove_assignment(
    assignment_id: str,
    current_user: Dict[str, Any] = Depends(require_any_leadership)
):
    """Remove role assignment (requires leadership role)"""
    try:
        result = await role_service.remove_assignment(assignment_id, current_user["id"])
        return result
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Remove assignment endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Assignment removal failed")

@router.get("/assignments/{assignment_id}", response_model=ExecutiveAssignmentResponse)
async def get_assignment(
    assignment_id: str,
    current_user: Dict[str, Any] = Depends(require_any_leadership)
):
    """Get assignment details by ID"""
    try:
        assignment = await role_service.get_assignment(assignment_id)
        if not assignment:
            raise NotFoundException("Assignment not found")
        return assignment
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        logger.error(f"Get assignment endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch assignment")

@router.get("/assignments/user/{user_id}", response_model=List[ExecutiveAssignmentResponse])
async def get_user_assignments(
    user_id: str,
    active_only: bool = Query(True, description="Show only active assignments"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get user's role assignments"""
    try:
        # Users can view their own assignments, leadership can view all
        if current_user["id"] != user_id:
            user_roles = [
                assignment.get("roles", {}).get("name")
                for assignment in current_user.get("executive_assignments", [])
                if assignment.get("is_active")
            ]
            
            if not any(role in ["Chairman", "Secretary", "Branch Chairman", "Branch Secretary"] for role in user_roles):
                raise AuthorizationException("Not authorized to view user assignments")
        
        assignments = await role_service.list_user_assignments(user_id, active_only)
        return assignments
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Get user assignments endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch assignments")

@router.get("/assignments/user/{user_id}/summary", response_model=RoleAssignmentList)
async def get_user_assignments_summary(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get user's role assignments with summary"""
    try:
        # Users can view their own assignments, leadership can view all
        if current_user["id"] != user_id:
            user_roles = [
                assignment.get("roles", {}).get("name")
                for assignment in current_user.get("executive_assignments", [])
                if assignment.get("is_active")
            ]
            
            if not any(role in ["Chairman", "Secretary", "Branch Chairman", "Branch Secretary"] for role in user_roles):
                raise AuthorizationException("Not authorized to view user assignments")
        
        assignments = await role_service.list_user_assignments(user_id, active_only=True)
        
        return RoleAssignmentList(
            assignments=assignments,
            total=len(assignments)
        )
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Get user assignments summary endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch assignments summary")

@router.get("/my-assignments", response_model=List[ExecutiveAssignmentResponse])
async def get_my_assignments(
    active_only: bool = Query(True, description="Show only active assignments"),
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get current user's role assignments"""
    try:
        assignments = await role_service.list_user_assignments(current_user["id"], active_only)
        return assignments
    except Exception as e:
        logger.error(f"Get my assignments endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch assignments")

@router.post("/assignments/bulk", response_model=List[ExecutiveAssignmentResponse])
async def bulk_assign_roles(
    assignments_data: List[ExecutiveAssignmentCreate],
    current_user: Dict[str, Any] = Depends(require_chapter_leadership)
):
    """Bulk assign roles to users (requires chapter leadership)"""
    try:
        results = []
        for assignment_data in assignments_data:
            try:
                assignment = await role_service.assign_role(assignment_data, current_user["id"])
                results.append(assignment)
            except Exception as e:
                logger.error(f"Bulk assignment failed for {assignment_data.user_id}: {e}")
                # Continue with other assignments
                continue
        
        return results
    except Exception as e:
        logger.error(f"Bulk assign roles endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Bulk role assignment failed")

@router.post("/assignments/{assignment_id}/deactivate", response_model=Dict[str, Any])
async def deactivate_assignment(
    assignment_id: str,
    current_user: Dict[str, Any] = Depends(require_any_leadership)
):
    """Deactivate role assignment (soft delete)"""
    try:
        update_data = ExecutiveAssignmentUpdate(is_active=False)
        await role_service.update_assignment(assignment_id, update_data, current_user["id"])
        return {"message": "Assignment deactivated successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except Exception as e:
        logger.error(f"Deactivate assignment endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Assignment deactivation failed")