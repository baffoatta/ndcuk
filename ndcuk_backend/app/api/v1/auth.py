from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any
from app.models.auth import (
    UserRegister, UserLogin, SocialLogin, Token, TokenRefresh,
    PasswordReset, PasswordResetConfirm, EmailVerification
)
from app.services.auth_service import auth_service
from app.api.dependencies import get_current_user
from app.core.exceptions import ValidationException, AuthenticationException
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.get("/registration-info", response_model=Dict[str, Any])
async def get_registration_info():
    """Get registration form information (branches, gender options, etc.)"""
    from app.utils.constants import AVAILABLE_BRANCHES, GENDER_OPTIONS, QUALIFICATION_CATEGORIES
    
    return {
        "available_branches": AVAILABLE_BRANCHES,
        "gender_options": GENDER_OPTIONS,
        "qualification_categories": QUALIFICATION_CATEGORIES,
        "password_requirements": {
            "min_length": 8,
            "required": ["uppercase", "lowercase", "digit"]
        },
        "age_requirement": {
            "minimum_age": 18
        }
    }

@router.post("/register", response_model=Dict[str, Any])
async def register(user_data: UserRegister):
    """Register a new user with email and password"""
    try:
        result = await auth_service.register_user(user_data)
        return result
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Registration endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Registration failed")

@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """Login user with email and password"""
    try:
        token = await auth_service.login_user(login_data)
        return token
    except AuthenticationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Login endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Login failed")

@router.post("/social-login", response_model=Token)
async def social_login(social_data: SocialLogin):
    """Login with social providers (Google/Apple)"""
    try:
        token = await auth_service.social_login(social_data)
        return token
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except AuthenticationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Social login endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Social login failed")

@router.post("/refresh", response_model=Token)
async def refresh_token(token_data: TokenRefresh):
    """Refresh access token using refresh token"""
    try:
        new_token = await auth_service.refresh_access_token(token_data.refresh_token)
        return new_token
    except AuthenticationException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Token refresh failed")

@router.post("/verify-email", response_model=Dict[str, Any])
async def verify_email(verification_data: EmailVerification):
    """Verify user email address"""
    try:
        result = await auth_service.verify_email(verification_data.token)
        return result
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Email verification endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email verification failed")

@router.post("/forgot-password", response_model=Dict[str, Any])
async def forgot_password(reset_data: PasswordReset):
    """Request password reset"""
    try:
        result = await auth_service.request_password_reset(reset_data.email)
        return result
    except Exception as e:
        logger.error(f"Password reset request endpoint error: {e}")
        # Always return success message for security
        return {"message": "If an account with this email exists, a password reset link has been sent."}

@router.post("/reset-password", response_model=Dict[str, Any])
async def reset_password(reset_data: PasswordResetConfirm):
    """Reset password with token"""
    try:
        result = await auth_service.reset_password(reset_data.token, reset_data.new_password)
        return result
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        logger.error(f"Password reset endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Password reset failed")

@router.post("/logout", response_model=Dict[str, Any])
async def logout(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Logout current user"""
    try:
        result = await auth_service.logout_user("")
        return result
    except Exception as e:
        logger.error(f"Logout endpoint error: {e}")
        return {"message": "Logged out successfully"}

@router.get("/me", response_model=Dict[str, Any])
async def get_current_user_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user information"""
    try:
        # Remove sensitive information
        user_info = {
            "id": current_user["id"],
            "full_name": current_user["full_name"],
            "email": current_user.get("email"),
            "phone": current_user.get("phone"),
            "address": current_user.get("address"),
            "date_of_birth": current_user.get("date_of_birth"),
            "membership_number": current_user.get("membership_number"),
            "status": current_user["status"],
            "email_verified": current_user["email_verified"],
            "avatar_url": current_user.get("avatar_url"),
            "memberships": current_user.get("memberships", []),
            "executive_assignments": current_user.get("executive_assignments", []),
            "created_at": current_user["created_at"],
            "updated_at": current_user["updated_at"]
        }
        
        return user_info
    except Exception as e:
        logger.error(f"Get current user endpoint error: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch user information")