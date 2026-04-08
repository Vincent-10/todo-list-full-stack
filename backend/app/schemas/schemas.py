"""
Pydantic schemas for request/response validation
"""
from datetime import datetime, date, time
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from enum import IntEnum


# =====================================================
# Enums
# =====================================================

class TaskStatus(IntEnum):
    """Task status enum"""
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2
    CANCELLED = 3


class TaskPriority(IntEnum):
    """Task priority enum"""
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4


# =====================================================
# User Schemas
# =====================================================

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=2, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    avatar_url: Optional[str] = None
    status: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload"""
    user_id: Optional[int] = None


# =====================================================
# Category Schemas
# =====================================================

class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#3B82F6", pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating category"""
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    """Schema for updating category"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")
    icon: Optional[str] = None
    sort_order: Optional[int] = None


class CategoryResponse(CategoryBase):
    """Schema for category response"""
    id: int
    user_id: int
    sort_order: int
    is_default: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# Tag Schemas
# =====================================================

class TagBase(BaseModel):
    """Base tag schema"""
    name: str = Field(..., min_length=1, max_length=30)
    color: str = Field(default="#10B981", pattern=r"^#[0-9A-Fa-f]{6}$")


class TagCreate(TagBase):
    """Schema for creating tag"""
    pass


class TagUpdate(BaseModel):
    """Schema for updating tag"""
    name: Optional[str] = Field(None, min_length=1, max_length=30)
    color: Optional[str] = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class TagResponse(TagBase):
    """Schema for tag response"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# =====================================================
# Task Schemas
# =====================================================

class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.LOW
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    reminder_at: Optional[datetime] = None
    is_starred: int = 0


class TaskCreate(TaskBase):
    """Schema for creating task"""
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = []


class TaskUpdate(BaseModel):
    """Schema for updating task"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    category_id: Optional[int] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    reminder_at: Optional[datetime] = None
    is_starred: Optional[int] = None
    sort_order: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class TaskResponse(TaskBase):
    """Schema for task response"""
    id: int
    user_id: int
    category_id: Optional[int] = None
    sort_order: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True


# =====================================================
# Filter/Query Schemas
# =====================================================

class TaskFilter(BaseModel):
    """Schema for task filtering"""
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    is_starred: Optional[bool] = None
    due_date_start: Optional[date] = None
    due_date_end: Optional[date] = None
    search: Optional[str] = None


# =====================================================
# Common Response Schemas
# =====================================================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str


class PaginatedResponse(BaseModel):
    """Paginated response wrapper"""
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int
