from flask import Flask, request, jsonify
import sqlite3
import datetime
from typing import Optional

app = Flask(__name__)
DATABASE = 'todos.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            completed BOOLEAN DEFAULT FALSE,
            priority TEXT DEFAULT 'medium',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/todos', methods=['GET'])
def list_todos():
    completed = request.args.get('completed')
    conn = get_db()
    cursor = conn.cursor()
    query = 'SELECT * FROM todos'
    params = []
    if completed is not None:
        query += ' WHERE completed = ?'
        params.append(1 if completed.lower() == 'true' else 0)
    cursor.execute(query, params)
    todos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(todos), 200

@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(dict(row)), 200

@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    if not data or 'title' not in data or not data['title'].strip():
        return jsonify({'error': 'Title is required and cannot be empty'}), 400
    
    title = data['title'].strip()
    if len(title) > 200:
        return jsonify({'error': 'Title must be 200 characters or less'}), 400
    
    description = data.get('description', '')
    priority = data.get('priority', 'medium')
    if priority not in ['low', 'medium', 'high']:
        priority = 'medium'
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO todos (title, description, priority)
        VALUES (?, ?, ?)
    ''', (title, description, priority))
    conn.commit()
    todo_id = cursor.lastrowid
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    row = cursor.fetchone()
    conn.close()
    return jsonify(dict(row)), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'error': 'Todo not found'}), 404
    
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
        params.append(data['description'])
    
    if 'completed' in data:
        updates.append('completed = ?')
        params.append(bool(data['completed']))
    
    if 'priority' in data:
        priority = data['priority']
        if priority not in ['low', 'medium', 'high']:
            priority = 'medium'
        updates.append('priority = ?')
        params.append(priority)
    
    if not updates:
        conn.close()
        return jsonify({'error': 'No valid fields to update'}), 400
    
    params.append(todo_id)
    query = f'UPDATE todos SET {', '.join(updates)} WHERE id = ?'
    cursor.execute(query, params)
    conn.commit()
    
    cursor.execute('SELECT * FROM todos WHERE id = ?', (todo_id,))
    row = cursor.fetchone()
    conn.close()
    return jsonify(dict(row)), 200

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM todos WHERE id = ?', (todo_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Todo not found'}), 404
    conn.close()
    return jsonify({'message': 'deleted'}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
