from flask import Flask, request, jsonify
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any

app = Flask(__name__)
DATABASE = 'todos.db'

# Database initialization
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT 0,
                priority TEXT DEFAULT 'medium',
                created_at TEXT NOT NULL
            )
        ''')
        conn.commit()

# Database helper functions
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        'id': row['id'],
        'title': row['title'],
        'description': row['description'],
        'completed': bool(row['completed']),
        'priority': row['priority'],
        'created_at': row['created_at']
    }

# Initialize database on startup
init_db()

# Error handling
def error_response(message: str, status_code: int):
    return jsonify({'error': message}), status_code

# GET /todos - List all todos
@app.route('/todos', methods=['GET'])
def get_todos():
    completed_filter = request.args.get('completed')
    
    query = 'SELECT * FROM todos'
    params = []
    
    if completed_filter is not None:
        if completed_filter.lower() == 'true':
            query += ' WHERE completed = 1'
        elif completed_filter.lower() == 'false':
            query += ' WHERE completed = 0'
        else:
            return error_response('Invalid completed parameter. Use true or false.', 400)
    
    query += ' ORDER BY id'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    
    todos = [row_to_dict(row) for row in rows]
    return jsonify(todos)

# GET /todos/<id> - Get a single todo
@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return error_response('Todo not found', 404)
    
    return jsonify(row_to_dict(row))

# POST /todos - Create a new todo
@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return error_response('Title is required', 400)
    
    title = data.get('title', '').strip()
    if not title:
        return error_response('Title cannot be empty', 400)
    
    if len(title) > 200:
        return error_response('Title must be 200 characters or less', 400)
    
    description = data.get('description', '')
    priority = data.get('priority', 'medium')
    
    # Validate priority
    if priority not in ['low', 'medium', 'high']:
        return error_response('Priority must be low, medium, or high', 400)
    
    created_at = datetime.now().isoformat()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO todos (title, description, priority, created_at)
        VALUES (?, ?, ?, ?)
    ''', (title, description, priority, created_at))
    
    todo_id = cursor.lastrowid
    conn.commit()
    
    # Fetch the created todo
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    row = cursor.fetchone()
    conn.close()
    
    return jsonify(row_to_dict(row)), 201

# PUT /todos/<id> - Update a todo
@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id: int):
    data = request.get_json()
    
    if not data:
        return error_response('No data provided', 400)
    
    # Check if todo exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        return error_response('Todo not found', 404)
    
    # Build update query
    updates = []
    params = []
    
    if 'title' in data:
        title = data['title'].strip()
        if not title:
            conn.close()
            return error_response('Title cannot be empty', 400)
        if len(title) > 200:
            conn.close()
            return error_response('Title must be 200 characters or less', 400)
        updates.append('title = ?')
        params.append(title)
    
    if 'description' in data:
        updates.append('description = ?')
        params.append(data['description'])
    
    if 'completed' in data:
        completed = data['completed']
        if not isinstance(completed, bool):
            conn.close()
            return error_response('Completed must be a boolean', 400)
        updates.append('completed = ?')
        params.append(1 if completed else 0)
    
    if 'priority' in data:
        priority = data['priority']
        if priority not in ['low', 'medium', 'high']:
            conn.close()
            return error_response('Priority must be low, medium, or high', 400)
        updates.append('priority = ?')
        params.append(priority)
    
    if not updates:
        conn.close()
        return error_response('No valid fields to update', 400)
    
    # Execute update
    params.append(todo_id)
    query = f'UPDATE todos SET {', '.join(updates)} WHERE id = ?'
    cursor.execute(query, params)
    conn.commit()
    
    # Fetch updated todo
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    row = cursor.fetchone()
    conn.close()
    
    return jsonify(row_to_dict(row))

# DELETE /todos/<id> - Delete a todo
@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if todo exists
    cursor.execute('SELECT id FROM todos WHERE id = ?', (todo_id,))
    row = cursor.fetchone()
    
    if row is None:
        conn.close()
        return error_response('Todo not found', 404)
    
    # Delete todo
    cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'deleted'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
