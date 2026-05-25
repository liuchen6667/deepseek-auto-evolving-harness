#!/usr/bin/env python3
"""
TODO REST API
A simple REST API for managing TODO items with SQLite storage.
"""

import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify, g
from flask_cors import CORS

def get_db():
    """Get SQLite database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('todos.db')
        # Return rows as dictionaries
        db.row_factory = sqlite3.Row
    return db


def init_db():
    """Initialize database with schema."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT 0,
                priority TEXT DEFAULT 'medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()


def close_db(error):
    """Close database connection at the end of request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def row_to_dict(row):
    """Convert SQLite row to dictionary."""
    if row is None:
        return None
    
    result = dict(row)
    # Convert boolean value
    result['completed'] = bool(result['completed'])
    # Convert datetime to ISO format string
    if result.get('created_at'):
        if isinstance(result['created_at'], str):
            # Already a string
            pass
        else:
            result['created_at'] = result['created_at'].isoformat()
    return result


# Create Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.teardown_appcontext(close_db)

# Initialize database
init_db()


@app.route('/')
def index():
    """Root endpoint."""
    return jsonify({
        'message': 'TODO API',
        'endpoints': [
            'GET /todos',
            'GET /todos/<id>',
            'POST /todos',
            'PUT /todos/<id>',
            'DELETE /todos/<id>'
        ]
    })


@app.route('/todos', methods=['GET'])
def get_todos():
    """Get all todos, optionally filtered by completion status."""
    completed_filter = request.args.get('completed')
    
    db = get_db()
    cursor = db.cursor()
    
    if completed_filter is not None:
        if completed_filter.lower() == 'true':
            cursor.execute('SELECT * FROM todos WHERE completed = 1 ORDER BY id')
        elif completed_filter.lower() == 'false':
            cursor.execute('SELECT * FROM todos WHERE completed = 0 ORDER BY id')
        else:
            return jsonify({'error': 'completed parameter must be true or false'}), 400
    else:
        cursor.execute('SELECT * FROM todos ORDER BY id')
    
    todos = [row_to_dict(row) for row in cursor.fetchall()]
    return jsonify(todos)


@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    """Get a single todo by ID."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    todo = cursor.fetchone()
    
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    return jsonify(row_to_dict(todo))


@app.route('/todos', methods=['POST'])
def create_todo():
    """Create a new todo."""
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
    
    # Validate priority
    valid_priorities = ['low', 'medium', 'high']
    if priority not in valid_priorities:
        return jsonify({'error': 'Priority must be low, medium, or high'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        INSERT INTO todos (title, description, priority)
        VALUES (?, ?, ?)
    ''', (title, description, priority))
    
    db.commit()
    
    # Get the newly created todo
    todo_id = cursor.lastrowid
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    new_todo = cursor.fetchone()
    
    return jsonify(row_to_dict(new_todo)), 201


@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """Update an existing todo."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Check if todo exists
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    existing_todo = cursor.fetchone()
    
    if existing_todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    # Prepare update fields
    update_fields = []
    update_values = []
    
    if 'title' in data:
        title = data['title'].strip()
        if not title:
            return jsonify({'error': 'Title cannot be empty'}), 400
        if len(title) > 200:
            return jsonify({'error': 'Title must be 200 characters or less'}), 400
        update_fields.append('title = ?')
        update_values.append(title)
    
    if 'description' in data:
        description = data['description'].strip()
        update_fields.append('description = ?')
        update_values.append(description)
    
    if 'completed' in data:
        completed = data['completed']
        if not isinstance(completed, bool):
            return jsonify({'error': 'Completed must be a boolean'}), 400
        update_fields.append('completed = ?')
        update_values.append(1 if completed else 0)
    
    if 'priority' in data:
        priority = data['priority'].lower()
        valid_priorities = ['low', 'medium', 'high']
        if priority not in valid_priorities:
            return jsonify({'error': 'Priority must be low, medium, or high'}), 400
        update_fields.append('priority = ?')
        update_values.append(priority)
    
    if not update_fields:
        return jsonify({'error': 'No valid fields to update'}), 400
    
    # Build and execute update query
    update_values.append(todo_id)
    update_query = f'UPDATE todos SET {", ".join(update_fields)} WHERE id = ?'
    
    cursor.execute(update_query, update_values)
    db.commit()
    
    # Get updated todo
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    updated_todo = cursor.fetchone()
    
    return jsonify(row_to_dict(updated_todo))


@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """Delete a todo."""
    db = get_db()
    cursor = db.cursor()
    
    # Check if todo exists
    cursor.execute('SELECT id FROM todos WHERE id = ?', (todo_id,))
    if cursor.fetchone() is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    db.commit()
    
    return jsonify({'message': 'deleted'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
