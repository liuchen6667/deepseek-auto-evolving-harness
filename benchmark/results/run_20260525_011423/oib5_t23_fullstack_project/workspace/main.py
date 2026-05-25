from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional, List
import os

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database models
class TodoDB(Base):
    __tablename__ = "todos"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False)
    priority = Column(String(10), default="medium")
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[str] = Field("medium", pattern="^(low|medium|high)$")
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=500)
    completed: Optional[bool] = None
    priority: Optional[str] = Field(None, pattern="^(low|medium|high)$")
    
    @validator('title')
    def title_not_empty_if_present(cls, v):
        if v is not None and not v.strip():
            raise ValueError('Title cannot be empty')
        if v is not None:
            return v.strip()
        return v

class TodoResponse(TodoBase):
    id: int
    completed: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# FastAPI app
app = FastAPI(title="TODO API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API endpoints
@app.get("/todos", response_model=List[TodoResponse])
def list_todos(completed: Optional[bool] = None, db: Session = Depends(get_db)):
    """Get all todos, optionally filtered by completion status"""
    query = db.query(TodoDB)
    if completed is not None:
        query = query.filter(TodoDB.completed == completed)
    todos = query.order_by(TodoDB.created_at.desc()).all()
    return todos

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """Get a single todo by ID"""
    todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo"""
    db_todo = TodoDB(
        title=todo.title,
        description=todo.description,
        priority=todo.priority
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate, db: Session = Depends(get_db)):
    """Update an existing todo"""
    db_todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Update only provided fields
    update_data = todo_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete a todo"""
    db_todo = db.query(TodoDB).filter(TodoDB.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    return {"message": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)