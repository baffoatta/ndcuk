from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime, date
from app.utils.constants import AVAILABLE_BRANCHES, GENDER_OPTIONS

class UserRegister(BaseModel):
    # Basic info
    email: EmailStr
    password: str
    full_name: str
    
    # Personal details
    gender: str
    date_of_birth: date
    occupation: str
    qualification: str
    address: str  # House address - now required
    
    # Branch selection (by name)
    branch_name: str
    
    # Profile picture (optional)
    profile_picture: Optional[str] = None  # Will store file path or URL
    
    @validator('gender')
    def validate_gender(cls, v):
        if v not in GENDER_OPTIONS:
            raise ValueError(f'Gender must be one of: {", ".join(GENDER_OPTIONS)}')
        return v
    
    @validator('branch_name')
    def validate_branch(cls, v):
        if v not in AVAILABLE_BRANCHES:
            raise ValueError(f'Branch "{v}" is not available. Available branches: {", ".join(AVAILABLE_BRANCHES)}')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @validator('date_of_birth')
    def validate_age(cls, v):
        from datetime import date
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 18:
            raise ValueError('User must be at least 18 years old')
        if age > 120:
            raise ValueError('Invalid date of birth')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class SocialLogin(BaseModel):
    provider: str
    token: str
    branch_id: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class EmailVerification(BaseModel):
    token: str