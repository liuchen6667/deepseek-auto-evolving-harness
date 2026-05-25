from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
import sqlite3
from contextlib import contextmanager
import json

# Database setup
DATABASE = "todos.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT 0,
            priority TEXT DEFAULT 'medium',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

# Pydantic models
class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    priority: Optional[str] = Field(default="medium", regex="^(low|medium|high)$")
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('title cannot be empty')
        return v.strip()

class TodoUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    priority: Optional[str] = Field(None, regex="^(low|medium|high)$")
    
    @validator('title')
    def title_not_empty_if_present(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('title cannot be empty')
            return v.strip()
        return v

class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool
    priority: str
    created_at: str
    
    class Config:
        orm_mode = True

# FastAPI app
app = FastAPI(title="TODO API", version="1.0.0")

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()

# Helper functions
def row_to_dict(row):
    return dict(row)

def format_datetime(dt_str):
    # SQLite returns string, ensure it's in ISO format
    if dt_str and isinstance(dt_str, str):
        # Try to parse and reformat
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt.isoformat()
        except:
            return dt_str
    return dt_str

# API endpoints
@app.get("/todos", response_model=List[TodoResponse])
def list_todos(completed: Optional[bool] = None):
    with get_db() as conn:
        cursor = conn.cursor()
        
        if completed is None:
            cursor.execute("SELECT * FROM todos ORDER BY created_at DESC")
        else:
            cursor.execute(
                "SELECT * FROM todos WHERE completed = ? ORDER BY created_at DESC",
                (1 if completed else 0,)
            )
        
        todos = []
        for row in cursor.fetchall():
            todo = row_to_dict(row)
            todo["completed"] = bool(todo["completed"])
            todo["created_at"] = format_datetime(todo["created_at"])
            todos.append(todo)
        
        return todos

@app.get("/todos/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        todo = row_to_dict(row)
        todo["completed"] = bool(todo["completed"])
        todo["created_at"] = format_datetime(todo["created_at"])
        return todo

@app.post("/todos", response_model=TodoResponse, status_code=201)
def create_todo(todo: TodoCreate):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO todos (title, description, priority)
            VALUES (?, ?, ?)
            """,
            (todo.title, todo.description, todo.priority)
        )
        conn.commit()
        
        todo_id = cursor.lastrowid
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        row = cursor.fetchone()
        
        todo_dict = row_to_dict(row)
        todo_dict["completed"] = bool(todo_dict["completed"])
        todo_dict["created_at"] = format_datetime(todo_dict["created_at"])
        return todo_dict

@app.put("/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo_update: TodoUpdate):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if todo exists
        cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Todo not found")
        
        # Build update query dynamically based on provided fields
        update_fields = []
        update_values = []
        
        if todo_update.title is not None:
            update_fields.append("title = ?")
            update_values.append(todo_update.title)
        if todo_update.description is not None:
            update_fields.append("description = ?")
            update_values.append(todo_update.description)
        if todo_update.completed is not None:
            update_fields.append("completed = ?")
            update_values.append(1 if todo_update.completed else 0)
        if todo_update.priority is not None:
            update_fields.append("priority = ?")
            update_values.append(todo_update.priority)
        
        if not update_fields:
            # No fields to update, just return existing todo
            cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        else:
            update_values.append(todo_id)
            update_query = f"UPDATE todos SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(update_query, update_values)
            conn.commit()
            cursor.execute("SELECT * FROM todos WHERE id = ?", (todo_id,))
        
        row = cursor.fetchone()
        todo_dict = row_to_dict(row)
        todo_dict["completed"] = bool(todo_dict["completed"])
        todo_dict["created_at"] = format_datetime(todo_dict["created_at"])
        return todo_dict

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if todo exists
        cursor.execute("SELECT id FROM todos WHERE id = ?", (todo_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Todo not found")
        
        cursor.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
        conn.commit()
        
        return {"message": "deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)