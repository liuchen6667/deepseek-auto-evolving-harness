from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum

class PriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TodoCreate(BaseModel):
    """Model for creating a new todo"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[PriorityEnum] = Field(PriorityEnum.MEDIUM)
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

class TodoUpdate(BaseModel):
    """Model for updating an existing todo"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    completed: Optional[bool] = None
    priority: Optional[PriorityEnum] = None
    
    @validator('title')
    def title_not_empty_if_present(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Title cannot be empty')
            return v.strip()
        return v

class TodoResponse(BaseModel):
    """Model for todo response"""
    id: int
    title: str
    description: str
    completed: bool
    priority: str
    created_at: str
    
    class Config:
        orm_mode = True