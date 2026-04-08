"""
Tag API endpoints
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.models import User, Tag
from app.schemas.schemas import TagCreate, TagUpdate, TagResponse, MessageResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=List[TagResponse])
async def get_tags(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all tags for current user
    """
    result = await db.execute(
        select(Tag)
        .where(Tag.user_id == current_user.id)
        .order_by(Tag.name)
    )
    tags = result.scalars().all()
    return tags


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new tag
    """
    # Check if tag name already exists for this user
    result = await db.execute(
        select(Tag).where(
            Tag.user_id == current_user.id,
            Tag.name == tag_data.name
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag with this name already exists"
        )
    
    tag = Tag(
        user_id=current_user.id,
        name=tag_data.name,
        color=tag_data.color
    )
    db.add(tag)
    await db.flush()
    await db.refresh(tag)
    return tag


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific tag
    """
    result = await db.execute(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == current_user.id
        )
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    return tag


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update a tag
    """
    result = await db.execute(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == current_user.id
        )
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Check if new name conflicts with existing tag
    if tag_data.name and tag_data.name != tag.name:
        result = await db.execute(
            select(Tag).where(
                Tag.user_id == current_user.id,
                Tag.name == tag_data.name
            )
        )
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag with this name already exists"
            )
    
    # Update fields
    update_data = tag_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tag, field, value)
    
    await db.flush()
    await db.refresh(tag)
    return tag


@router.delete("/{tag_id}", response_model=MessageResponse)
async def delete_tag(
    tag_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a tag
    """
    result = await db.execute(
        select(Tag).where(
            Tag.id == tag_id,
            Tag.user_id == current_user.id
        )
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    await db.delete(tag)
    return {"message": "Tag deleted successfully"}
