from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db, create_tables
import models
import database

app = FastAPI(title="TODO API", description="A simple REST API for managing TODO items")

# Create tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

@app.get("/todos", response_model=list[models.TodoResponse])
def get_todos(
    completed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all todos, optionally filtered by completion status"""
    query = db.query(database.Todo)
    if completed is not None:
        query = query.filter(database.Todo.completed == completed)
    todos = query.order_by(database.Todo.created_at.desc()).all()
    return todos

@app.get("/todos/{todo_id}", response_model=models.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """Get a single todo by ID"""
    todo = db.query(database.Todo).filter(database.Todo.id == todo_id).first()
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    return todo

@app.post("/todos", response_model=models.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: models.TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo"""
    db_todo = database.Todo(
        title=todo.title,
        description=todo.description,
        priority=todo.priority
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.put("/todos/{todo_id}", response_model=models.TodoResponse)
def update_todo(todo_id: int, todo_update: models.TodoUpdate, db: Session = Depends(get_db)):
    """Update an existing todo"""
    db_todo = db.query(database.Todo).filter(database.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    # Update only provided fields
    update_data = todo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)
    
    db.commit()
    db.refresh(db_todo)
    return db_todo

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete a todo"""
    db_todo = db.query(database.Todo).filter(database.Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found"
        )
    
    db.delete(db_todo)
    db.commit()
    return JSONResponse(
        content={"message": "deleted"},
        status_code=status.HTTP_200_OK
    )

@app.get("/")
def root():
    return {"message": "TODO API is running. Visit /docs for API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)