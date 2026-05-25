from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import create_engine
import os

# Database setup
DATABASE_URL = "sqlite:///./todos.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy model
class TodoModel(Base):
    __tablename__ = "todos"
    
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    title = sa.Column(sa.String(200), nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    completed = sa.Column(sa.Boolean, default=False)
    priority = sa.Column(sa.String(10), default="medium")
    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = Field(default="medium")
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in ["low", "medium", "high"]:
            raise ValueError('Priority must be "low", "medium", or "high"')
        return v or "medium"

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = None
    
    @validator('priority')
    def validate_priority(cls, v):
        if v and v not in ["low", "medium", "high"]:
            raise ValueError('Priority must be "low", "medium", or "high"')
        return v

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    created_at: datetime
    
    class Config:
        orm_mode = True

# FastAPI app
app = FastAPI(title="TODO API", description="A simple REST API for managing TODO items")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API endpoints
@app.get("/todos", response_model=List[TodoResponse])
def get_todos(completed: Optional[bool] = None, db: Session = Depends(get_db)):
    """Get all todos, optionally filtered by completed status"""
    query = db.query(TodoModel)
    if completed is not None:
        query = query.filter(TodoModel.completed == completed)
    todos = query.order_by(TodoModel.created_at.desc()).all()
    return todos

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """Get a single todo by ID"""
    todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo"""
    db_todo = TodoModel(
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
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
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
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_todo)
    db.commit()
    return {"message": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)