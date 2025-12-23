"""
Pydantic Schemas Module
=======================
This module defines Pydantic models for request/response validation.
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


# ============== Book Schemas ==============

class BookBase(BaseModel):
    """Base schema with common book attributes"""
    title: str = Field(
        min_length=1,
        max_length=200,
        description="The title of the book",
        examples=["The Great Gatsby"]
    )
    author: str = Field(
        min_length=1,
        max_length=100,
        description="The author of the book",
        examples=["F. Scott Fitzgerald"]
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="A brief description of the book",
        examples=["A novel about the American Dream"]
    )
    rating: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Rating from 0 to 100",
        examples=[85]
    )


class BookCreate(BookBase):
    """Schema for creating a new book"""
    pass


class BookUpdate(BaseModel):
    """Schema for updating a book (all fields optional)"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    rating: Optional[int] = Field(None, ge=0, le=100)


class BookResponse(BookBase):
    """Schema for book responses (includes ID)"""
    id: int

    # Enable ORM mode for SQLAlchemy compatibility
    model_config = ConfigDict(from_attributes=True)


# ============== Message Schemas ==============

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    detail: Optional[str] = None


class DeleteResponse(BaseModel):
    """Response for delete operations"""
    message: str
    deleted_id: int
    deleted_title: str
