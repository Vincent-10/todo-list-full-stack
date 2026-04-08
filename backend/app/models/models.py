"""
SQLAlchemy models for the application
"""
from datetime import datetime, date, time
from typing import Optional, List
from sqlalchemy import (
    Column, BigInteger, String, Text, DateTime, Date, Time,
    SmallInteger, Integer, ForeignKey, Table, Index
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.db.database import Base


# Task-Tag association table
task_tags = Table(
    'task_tags',
    Base.metadata,
    Column('task_id', BigInteger, ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True),
    Column('tag_id', BigInteger, ForeignKey('tags.id', ondelete='CASCADE'), primary_key=True),
    Column('created_at', DateTime, default=datetime.utcnow),
)


class User(Base):
    """User model"""
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    status: Mapped[int] = mapped_column(SmallInteger, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    categories: Mapped[List["Category"]] = relationship("Category", back_populates="user", cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship("Tag", back_populates="user", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="user", cascade="all, delete-orphan")


class Category(Base):
    """Category model"""
    __tablename__ = 'categories'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    color: Mapped[str] = mapped_column(String(7), default='#3B82F6')
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_default: Mapped[int] = mapped_column(SmallInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="categories")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="category")
    
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_user_sort', 'user_id', 'sort_order'),
    )


class Tag(Base):
    """Tag model"""
    __tablename__ = 'tags'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    color: Mapped[str] = mapped_column(String(7), default='#10B981')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tags")
    tasks: Mapped[List["Task"]] = relationship("Task", secondary=task_tags, back_populates="tags")
    
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
    )


class Task(Base):
    """Task model"""
    __tablename__ = 'tasks'
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    category_id: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[int] = mapped_column(SmallInteger, default=0)  # 0-pending, 1-in_progress, 2-completed, 3-cancelled
    priority: Mapped[int] = mapped_column(SmallInteger, default=1)  # 0-none, 1-low, 2-medium, 3-high, 4-urgent
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    due_time: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    reminder_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_starred: Mapped[int] = mapped_column(SmallInteger, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="tasks")
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="tasks")
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=task_tags, back_populates="tasks")
    
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_category_id', 'category_id'),
        Index('idx_user_status', 'user_id', 'status'),
        Index('idx_user_priority', 'user_id', 'priority'),
        Index('idx_user_due_date', 'user_id', 'due_date'),
        Index('idx_user_starred', 'user_id', 'is_starred'),
    )
