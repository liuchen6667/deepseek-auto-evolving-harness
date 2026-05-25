from flask import Flask, request, jsonify
import sqlite3
import json
from datetime import datetime
from typing import Optional, Dict, Any

app = Flask(__name__)
DATABASE = 'todos.db'

def init_db():
    """Initialize the database with the todos table"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL CHECK(length(title) <= 200),
            description TEXT,
            completed BOOLEAN DEFAULT 0,
            priority TEXT DEFAULT 'medium' CHECK(priority IN ('low', 'medium', 'high')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def dict_factory(cursor, row):
    """Convert database row to dictionary"""
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    
    # Convert boolean value
    if 'completed' in d:
        d['completed'] = bool(d['completed'])
    
    # Convert timestamp to ISO format if needed
    if 'created_at' in d and d['created_at']:
        if isinstance(d['created_at'], str):
            # Already a string, ensure it's ISO format
            try:
                # Try to parse and reformat if needed
                dt = datetime.fromisoformat(d['created_at'].replace('Z', '+00:00'))
                d['created_at'] = dt.isoformat()
            except:
                pass
    
    return d

def get_db_connection():
    """Get database connection with dict factory"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = dict_factory
    return conn

@app.route('/todos', methods=['GET'])
def get_todos():
    """Get all todos, with optional completed filter"""
    completed_filter = request.args.get('completed')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if completed_filter is not None:
        if completed_filter.lower() == 'true':
            cursor.execute('SELECT * FROM todos WHERE completed = 1 ORDER BY id')
        elif completed_filter.lower() == 'false':
            cursor.execute('SELECT * FROM todos WHERE completed = 0 ORDER BY id')
        else:
            conn.close()
            return jsonify({'error': 'completed parameter must be "true" or "false"'}), 400
    else:
        cursor.execute('SELECT * FROM todos ORDER BY id')
    
    todos = cursor.fetchall()
    conn.close()
    
    return jsonify(todos), 200

@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a single todo by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    todo = cursor.fetchone()
    conn.close()
    
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    return jsonify(todo), 200

@app.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo"""
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'Title cannot be empty'}), 400
    
    if len(title) > 200:
        return jsonify({'error': 'Title must be 200 characters or less'}), 400
    
    description = data.get('description', '').strip()
    priority = data.get('priority', 'medium').lower()
    
    if priority not in ['low', 'medium', 'high']:
        priority = 'medium'
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO todos (title, description, priority)
            VALUES (?, ?, ?)
        ''', (title, description, priority))
        
        todo_id = cursor.lastrowid
        conn.commit()
        
        cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
        todo = cursor.fetchone()
        
        conn.close()
        return jsonify(todo), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update an existing todo"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if todo exists
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    todo = cursor.fetchone()
    
    if todo is None:
        conn.close()
        return jsonify({'error': 'Todo not found'}), 404
    
    # Build update query
    updates = []
    params = []
    
    if 'title' in data:
        title = data['title'].strip()
        if not title:
            conn.close()
            return jsonify({'error': 'Title cannot be empty'}), 400
        if len(title) > 200:
            conn.close()
            return jsonify({'error': 'Title must be 200 characters or less'}), 400
        updates.append('title = ?')
        params.append(title)
    
    if 'description' in data:
        updates.append('description = ?')
        params.append(data['description'].strip())
    
    if 'completed' in data:
        completed = data['completed']
        if not isinstance(completed, bool):
            conn.close()
            return jsonify({'error': 'completed must be a boolean'}), 400
        updates.append('completed = ?')
        params.append(1 if completed else 0)
    
    if 'priority' in data:
        priority = data['priority'].lower()
        if priority not in ['low', 'medium', 'high']:
            conn.close()
            return jsonify({'error': 'priority must be "low", "medium", or "high"'}), 400
        updates.append('priority = ?')
        params.append(priority)
    
    if not updates:
        conn.close()
        return jsonify({'error': 'No valid fields to update'}), 400
    
    # Execute update
    params.append(todo_id)
    update_query = f'UPDATE todos SET {", ".join(updates)} WHERE id = ?'
    
    try:
        cursor.execute(update_query, params)
        conn.commit()
        
        cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
        updated_todo = cursor.fetchone()
        
        conn.close()
        return jsonify(updated_todo), 200
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if todo exists
    cursor.execute('SELECT id FROM todos WHERE id = ?', (todo_id,))
    todo = cursor.fetchone()
    
    if todo is None:
        conn.close()
        return jsonify({'error': 'Todo not found'}), 404
    
    # Delete todo
    cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'deleted'}), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_db()
    print("Database initialized")
    print("Starting Flask server on http://127.0.0.1:5000")
    app.run(debug=True)
