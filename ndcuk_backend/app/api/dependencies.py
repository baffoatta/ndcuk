from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from app.core.security import verify_token
from app.services.auth_service import auth_service
from app.services.user_service import user_service
from app.core.exceptions import AuthenticationException
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current authenticated user"""
    try:
        # Verify token
        user_id = verify_token(credentials.credentials)
        if not user_id:
            raise AuthenticationException("Invalid token")
        
        # Get user with roles
        user_data = await auth_service.get_user_with_roles(user_id)
        if not user_data:
            raise AuthenticationException("User not found")
        
        return user_data
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get current active user (approved status)"""
    if current_user.get("status") not in ["approved"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account not approved"
        )
    return current_user

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[Dict[str, Any]]:
    """Get current user if token provided (optional)"""
    if not credentials:
        return None
    
    try:
        user_id = verify_token(credentials.credentials)
        if user_id:
            return await auth_service.get_user_with_roles(user_id)
    except Exception:
        pass
    
    return None

def require_roles(allowed_roles: list):
    """Dependency to check if user has required roles"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)):
        user_roles = []
        
        # Extract user roles from executive_assignments
        for assignment in current_user.get("executive_assignments", []):
            if assignment.get("is_active"):
                role_name = assignment.get("roles", {}).get("name")
                if role_name:
                    user_roles.append(role_name)
        
        # Check if user has any of the required roles
        if not any(role in user_roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Required roles: {allowed_roles}"
            )
        
        return current_user
    
    return role_checker

def require_permissions(required_permissions: Dict[str, list]):
    """Dependency to check if user has required permissions"""
    def permission_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)):
        user_permissions = {}
        
        # Extract user permissions from roles
        for assignment in current_user.get("executive_assignments", []):
            if assignment.get("is_active"):
                role_permissions = assignment.get("roles", {}).get("permissions", {})
                
                # Merge permissions
                for resource, actions in role_permissions.items():
                    if resource not in user_permissions:
                        user_permissions[resource] = []
                    
                    if isinstance(actions, list):
                        user_permissions[resource].extend(actions)
                    elif actions is True:
                        user_permissions[resource] = ["all"]
        
        # Check required permissions
        for resource, required_actions in required_permissions.items():
            user_actions = user_permissions.get(resource, [])
            
            if "all" in user_actions:
                continue
                
            if not any(action in user_actions for action in required_actions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Required permissions: {required_permissions}"
                )
        
        return current_user
    
    return permission_checker

async def get_user_branch_access(
    current_user: Dict[str, Any] = Depends(get_current_active_user)
) -> list:
    """Get list of branch IDs user has access to"""
    accessible_branches = []
    
    for assignment in current_user.get("executive_assignments", []):
        if assignment.get("is_active"):
            role_name = assignment.get("roles", {}).get("name")
            
            # Chapter-level roles have access to all branches
            if role_name in ["Chairman", "Secretary", "Vice Chairman"]:
                # Return all branches (would need to query from DB)
                return ["all"]
            
            # Branch-level roles have access to their branch
            if assignment.get("branch_id"):
                accessible_branches.append(assignment["branch_id"])
    
    return accessible_branches

# Role-specific dependencies
require_chapter_leadership = require_roles(["Chairman", "Secretary", "Vice Chairman"])
require_branch_leadership = require_roles(["Branch Chairman", "Branch Secretary"])  
require_any_leadership = require_roles([
    "Chairman", "Secretary", "Vice Chairman", 
    "Branch Chairman", "Branch Secretary"
])

# Permission-specific dependencies
require_member_management = require_permissions({"members": ["read", "write", "approve"]})
require_role_management = require_permissions({"roles": ["read", "write", "assign"]})
require_branch_management = require_permissions({"branches": ["read", "write"]})