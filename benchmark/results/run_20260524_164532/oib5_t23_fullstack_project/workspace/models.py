from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(default="")
    priority: Optional[str] = Field(default="medium")
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if v is not None and v not in ["low", "medium", "high"]:
            raise ValueError('priority must be low, medium, or high')
        return v

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = Field(default=None)
    
    @field_validator('priority')
    @classmethod
    def validate_priority(cls, v):
        if v is not None and v not in ["low", "medium", "high"]:
            raise ValueError('priority must be low, medium, or high')
        return v

class TodoResponse(TodoBase):
    id: int
    completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True