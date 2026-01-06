from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TodoBase(BaseModel):
    """Base Todo model with common fields."""
    name: str = Field(..., min_length=1, max_length=100, description="Todo name")
    description: str = Field(..., min_length=1, max_length=500, description="Todo description")
    complete: bool = Field(default=False, description="Completion status")


class TodoCreate(TodoBase):
    """Model for creating a new todo."""
    pass


class TodoUpdate(BaseModel):
    """Model for updating a todo (all fields optional)."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Todo name")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="Todo description")
    complete: Optional[bool] = Field(None, description="Completion status")


class TodoResponse(TodoBase):
    """Model for todo response with ID."""
    id: str = Field(..., description="Todo unique identifier")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        from_attributes = True


class TodoInDB(TodoBase):
    """Model for todo as stored in database."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Backward compatibility alias
Todo = TodoCreate