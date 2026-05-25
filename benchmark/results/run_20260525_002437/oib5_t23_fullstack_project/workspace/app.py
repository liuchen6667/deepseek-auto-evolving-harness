import sqlite3
import json
from datetime import datetime
from flask import Flask, request, jsonify, g

app = Flask(__name__)
DATABASE = 'todos.db'

# Database helper functions
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK(length(title) <= 200),
                description TEXT,
                completed BOOLEAN DEFAULT 0,
                priority TEXT CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        db.commit()

# Helper to convert row to dict
def row_to_dict(row):
    return {
        'id': row['id'],
        'title': row['title'],
        'description': row['description'],
        'completed': bool(row['completed']),
        'priority': row['priority'],
        'created_at': row['created_at']
    }

# Error handler
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': str(error.description) if hasattr(error, 'description') else 'Bad request'}), 400

# API endpoints
@app.route('/todos', methods=['GET'])
def get_todos():
    completed_filter = request.args.get('completed')
    
    db = get_db()
    cursor = db.cursor()
    
    if completed_filter is not None:
        if completed_filter.lower() == 'true':
            cursor.execute('SELECT * FROM todos WHERE completed = 1 ORDER BY id')
        elif completed_filter.lower() == 'false':
            cursor.execute('SELECT * FROM todos WHERE completed = 0 ORDER BY id')
        else:
            return jsonify({'error': 'completed parameter must be "true" or "false"'}), 400
    else:
        cursor.execute('SELECT * FROM todos ORDER BY id')
    
    todos = [row_to_dict(row) for row in cursor.fetchall()]
    return jsonify(todos)

@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    row = cursor.fetchone()
    
    if row is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    return jsonify(row_to_dict(row))

@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'title is required'}), 400
    
    title = data.get('title', '').strip()
    if not title:
        return jsonify({'error': 'title cannot be empty'}), 400
    
    if len(title) > 200:
        return jsonify({'error': 'title must be 200 characters or less'}), 400
    
    description = data.get('description', '')
    priority = data.get('priority', 'medium')
    
    if priority not in ['low', 'medium', 'high']:
        return jsonify({'error': 'priority must be low, medium, or high'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute('''
        INSERT INTO todos (title, description, priority)
        VALUES (?, ?, ?)
    ''', (title, description, priority))
    
    db.commit()
    
    new_id = cursor.lastrowid
    cursor.execute('SELECT * FROM todos WHERE id = ?', (new_id,))
    new_todo = cursor.fetchone()
    
    return jsonify(row_to_dict(new_todo)), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if todo exists
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    if cursor.fetchone() is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    # Build update query dynamically based on provided fields
    updates = []
    values = []
    
    if 'title' in data:
        title = data['title'].strip()
        if not title:
            return jsonify({'error': 'title cannot be empty'}), 400
        if len(title) > 200:
            return jsonify({'error': 'title must be 200 characters or less'}), 400
        updates.append('title = ?')
        values.append(title)
    
    if 'description' in data:
        updates.append('description = ?')
        values.append(data['description'])
    
    if 'completed' in data:
        completed = data['completed']
        if not isinstance(completed, bool):
            return jsonify({'error': 'completed must be a boolean'}), 400
        updates.append('completed = ?')
        values.append(1 if completed else 0)
    
    if 'priority' in data:
        priority = data['priority']
        if priority not in ['low', 'medium', 'high']:
            return jsonify({'error': 'priority must be low, medium, or high'}), 400
        updates.append('priority = ?')
        values.append(priority)
    
    if not updates:
        return jsonify({'error': 'No valid fields to update'}), 400
    
    values.append(todo_id)
    query = f'UPDATE todos SET {", ".join(updates)} WHERE id = ?'
    
    cursor.execute(query, values)
    db.commit()
    
    # Return updated todo
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    updated_todo = cursor.fetchone()
    
    return jsonify(row_to_dict(updated_todo))

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    db = get_db()
    cursor = db.cursor()
    
    # Check if todo exists
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    if cursor.fetchone() is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    db.commit()
    
    return jsonify({'message': 'deleted'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
