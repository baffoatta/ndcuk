from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class BranchStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"

class MembershipStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    LAPSED = "lapsed"
    SUSPENDED = "suspended"

class BranchBase(BaseModel):
    name: str
    location: str
    description: Optional[str] = None
    min_members: Optional[int] = 20

class BranchCreate(BranchBase):
    chapter_id: str

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    min_members: Optional[int] = None
    status: Optional[BranchStatus] = None

class BranchResponse(BranchBase):
    id: str
    chapter_id: str
    chapter_name: Optional[str] = None
    status: BranchStatus
    member_count: Optional[int] = 0
    created_by: Optional[str] = None
    created_by_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BranchListResponse(BaseModel):
    branches: List[BranchResponse]
    total: int

class MembershipBase(BaseModel):
    user_id: str
    branch_id: str

class MembershipCreate(MembershipBase):
    pass

class MembershipUpdate(BaseModel):
    status: Optional[MembershipStatus] = None
    card_issued: Optional[bool] = None

class MembershipResponse(MembershipBase):
    id: str
    status: MembershipStatus
    joined_date: datetime
    approved_by: Optional[str] = None
    approved_by_name: Optional[str] = None
    approved_at: Optional[datetime] = None
    card_issued: bool
    card_issued_at: Optional[datetime] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    branch_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BranchMembersResponse(BaseModel):
    members: List[MembershipResponse]
    total: int
    branch_id: str
    branch_name: str