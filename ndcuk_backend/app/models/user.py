from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, date
from enum import Enum

class UserStatus(str, Enum):
    NOT_APPROVED = "not_approved"
    PENDING_APPROVAL = "pending_approval" 
    APPROVED = "approved"
    SUSPENDED = "suspended"
    EXPIRED = "expired"

class UserBase(BaseModel):
    full_name: str
    address: str  # Now required
    date_of_birth: date  # Now required
    gender: Optional[str] = None
    occupation: Optional[str] = None
    qualification: Optional[str] = None

class UserCreate(UserBase):
    email: EmailStr
    password: str
    branch_id: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    address: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    qualification: Optional[str] = None
    avatar_url: Optional[str] = None

class UserResponse(UserBase):
    id: str
    email: str
    membership_number: Optional[str] = None
    status: UserStatus
    email_verified: bool
    avatar_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int

class UserStatusUpdate(BaseModel):
    status: UserStatus
    notes: Optional[str] = None