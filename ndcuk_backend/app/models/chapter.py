from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ChapterStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class ChapterBase(BaseModel):
    name: str
    country: str = "UK"
    description: Optional[str] = None

class ChapterCreate(ChapterBase):
    pass

class ChapterUpdate(BaseModel):
    name: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ChapterStatus] = None

class ChapterResponse(ChapterBase):
    id: str
    status: ChapterStatus
    branch_count: Optional[int] = 0
    member_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChapterListResponse(BaseModel):
    chapters: List[ChapterResponse]
    total: int