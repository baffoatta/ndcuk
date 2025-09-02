from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RoleScopeType(str, Enum):
    CHAPTER = "chapter"
    BRANCH = "branch"  
    BOTH = "both"

class RoleBase(BaseModel):
    name: str
    scope_type: RoleScopeType
    description: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = {}

class RoleCreate(RoleBase):
    category_id: Optional[str] = None

class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class RoleResponse(RoleBase):
    id: str
    category_id: Optional[str] = None
    category_name: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RoleCategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True

class ExecutiveAssignmentCreate(BaseModel):
    user_id: str
    role_id: str
    chapter_id: Optional[str] = None
    branch_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    notes: Optional[str] = None

class ExecutiveAssignmentUpdate(BaseModel):
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class ExecutiveAssignmentResponse(BaseModel):
    id: str
    user_id: str
    user_name: Optional[str] = None
    role_id: str
    role_name: str
    chapter_id: Optional[str] = None
    chapter_name: Optional[str] = None
    branch_id: Optional[str] = None
    branch_name: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool
    appointed_by: Optional[str] = None
    appointed_by_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class RoleAssignmentList(BaseModel):
    assignments: List[ExecutiveAssignmentResponse]
    total: int