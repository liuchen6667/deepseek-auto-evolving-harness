from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import database
import models

app = FastAPI(title="TODO API", description="A simple REST API for managing TODO items")

@app.get("/todos", response_model=List[models.TodoResponse])
def list_todos(
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    db: Session = Depends(database.get_db)
):
    """List all todos, optionally filtered by completion status"""
    query = db.query(database.Todo)
    if completed is not None:
        query = query.filter(database.Todo.completed == completed)
    todos = query.all()
    return [todo.to_dict() for todo in todos]

@app.get("/todos/{todo_id}", response_model=models.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(database.get_db)):
    """Get a single todo by ID"""
    todo = db.query(database.Todo).filter(database.Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo.to_dict()

@app.post("/todos", response_model=models.TodoResponse, status_code=201)
def create_todo(todo: models.TodoCreate, db: Session = Depends(database.get_db)):
    """Create a new todo"""
    # Create new todo object
    db_todo = database.Todo(
        title=todo.title,
        description=todo.description or "",
        priority=todo.priority.value if todo.priority else "medium"
    )
    
    # Save to database
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    
    return db_todo.to_dict()

@app.put("/todos/{todo_id}", response_model=models.TodoResponse)
def update_todo(todo_id: int, todo_update: models.TodoUpdate, db: Session = Depends(database.get_db)):
    """Update an existing todo"""
    # Find the todo
    db_todo = db.query(database.Todo).filter(database.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Update fields if provided
    if todo_update.title is not None:
        db_todo.title = todo_update.title
    if todo_update.description is not None:
        db_todo.description = todo_update.description
    if todo_update.completed is not None:
        db_todo.completed = todo_update.completed
    if todo_update.priority is not None:
        db_todo.priority = todo_update.priority.value
    
    # Save changes
    db.commit()
    db.refresh(db_todo)
    
    return db_todo.to_dict()

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(database.get_db)):
    """Delete a todo"""
    # Find the todo
    db_todo = db.query(database.Todo).filter(database.Todo.id == todo_id).first()
    if not db_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    # Delete from database
    db.delete(db_todo)
    db.commit()
    
    return {"message": "deleted"}

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)