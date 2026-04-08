"""
Task API endpoints
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.models import User, Task, Tag, Category
from app.schemas.schemas import (
    TaskCreate, TaskUpdate, TaskResponse, MessageResponse,
    TaskStatus, TaskPriority
)
from app.api.deps import get_current_user
import logging

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    category_id: Optional[int] = None,
    is_starred: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tasks for current user with optional filters
    """
    logging.info('ssss')
    query = (
        select(Task)
        .options(selectinload(Task.category), selectinload(Task.tags))
        .where(Task.user_id == current_user.id)
    )
    
    # Apply filters
    if status is not None:
        query = query.where(Task.status == status)
    if priority is not None:
        query = query.where(Task.priority == priority)
    if category_id is not None:
        query = query.where(Task.category_id == category_id)
    if is_starred is not None:
        query = query.where(Task.is_starred == (1 if is_starred else 0))
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern)
            )
        )
    
    # Apply ordering and pagination
    query = query.order_by(Task.sort_order, Task.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    tasks = result.scalars().all()
    return tasks


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new task
    """
    # Verify category belongs to user if provided
    if task_data.category_id:
        result = await db.execute(
            select(Category).where(
                Category.id == task_data.category_id,
                Category.user_id == current_user.id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found"
            )
    
    # Create task
    task = Task(
        user_id=current_user.id,
        category_id=task_data.category_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        due_date=task_data.due_date,
        due_time=task_data.due_time,
        reminder_at=task_data.reminder_at,
        is_starred=task_data.is_starred
    )
    
    # Add tags if provided
    if task_data.tag_ids:
        result = await db.execute(
            select(Tag).where(
                Tag.id.in_(task_data.tag_ids),
                Tag.user_id == current_user.id
            )
        )
        tags = result.scalars().all()
        task.tags = list(tags)
    
    db.add(task)
    await db.flush()
    
    # Reload with relationships
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.category), selectinload(Task.tags))
        .where(Task.id == task.id)
    )
    task = result.scalar_one()
    
    return task


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific task
    """
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.category), selectinload(Task.tags))
        .where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a task
    """
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.category), selectinload(Task.tags))
        .where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Verify category if being updated
    if task_data.category_id is not None:
        if task_data.category_id:
            result = await db.execute(
                select(Category).where(
                    Category.id == task_data.category_id,
                    Category.user_id == current_user.id
                )
            )
            if not result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category not found"
                )
    
    # Update fields
    update_data = task_data.model_dump(exclude_unset=True, exclude={"tag_ids"})
    
    # Handle status change to completed
    if "status" in update_data:
        if update_data["status"] == TaskStatus.COMPLETED and task.status != TaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()
        elif update_data["status"] != TaskStatus.COMPLETED:
            task.completed_at = None
    
    for field, value in update_data.items():
        setattr(task, field, value)
    
    # Update tags if provided
    if task_data.tag_ids is not None:
        result = await db.execute(
            select(Tag).where(
                Tag.id.in_(task_data.tag_ids),
                Tag.user_id == current_user.id
            )
        )
        tags = result.scalars().all()
        task.tags = list(tags)
    
    await db.flush()
    await db.refresh(task)
    
    return task


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a task
    """
    result = await db.execute(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    await db.delete(task)
    return {"message": "Task deleted successfully"}


@router.patch("/{task_id}/toggle-star", response_model=TaskResponse)
async def toggle_star(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle task starred status
    """
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.category), selectinload(Task.tags))
        .where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.is_starred = 0 if task.is_starred else 1
    await db.flush()
    await db.refresh(task)
    
    return task


@router.patch("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark task as completed
    """
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.category), selectinload(Task.tags))
        .where(
            Task.id == task_id,
            Task.user_id == current_user.id
        )
    )
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    await db.flush()
    await db.refresh(task)
    
    return task
