from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)

# Configure SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'todos.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Todo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    priority = db.Column(db.String(10), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# Create database tables
with app.app_context():
    db.create_all()

# Validation functions
def validate_priority(priority):
    if priority not in ['low', 'medium', 'high']:
        return False
    return True

def validate_todo_data(data, is_update=False):
    errors = []
    
    if not is_update and 'title' not in data:
        errors.append('title is required')
    elif 'title' in data:
        title = data['title']
        if not isinstance(title, str):
            errors.append('title must be a string')
        elif len(title.strip()) == 0:
            errors.append('title cannot be empty')
        elif len(title) > 200:
            errors.append('title must be 200 characters or less')
    
    if 'description' in data and data['description'] is not None:
        if not isinstance(data['description'], str):
            errors.append('description must be a string')
    
    if 'completed' in data and data['completed'] is not None:
        if not isinstance(data['completed'], bool):
            errors.append('completed must be a boolean')
    
    if 'priority' in data and data['priority'] is not None:
        if not isinstance(data['priority'], str):
            errors.append('priority must be a string')
        elif not validate_priority(data['priority']):
            errors.append('priority must be one of: low, medium, high')
    
    return errors

# Routes
@app.route('/todos', methods=['GET'])
def get_todos():
    completed_filter = request.args.get('completed')
    
    query = Todo.query
    
    if completed_filter is not None:
        if completed_filter.lower() == 'true':
            query = query.filter_by(completed=True)
        elif completed_filter.lower() == 'false':
            query = query.filter_by(completed=False)
    
    todos = query.order_by(Todo.created_at.desc()).all()
    return jsonify([todo.to_dict() for todo in todos])

@app.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())

@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    errors = validate_todo_data(data)
    if errors:
        return jsonify({'error': ', '.join(errors)}), 400
    
    todo = Todo(
        title=data['title'].strip(),
        description=data.get('description', ''),
        completed=data.get('completed', False),
        priority=data.get('priority', 'medium')
    )
    
    db.session.add(todo)
    db.session.commit()
    
    return jsonify(todo.to_dict()), 201

@app.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Request body must be JSON'}), 400
    
    errors = validate_todo_data(data, is_update=True)
    if errors:
        return jsonify({'error': ', '.join(errors)}), 400
    
    if 'title' in data:
        todo.title = data['title'].strip()
    if 'description' in data:
        todo.description = data['description']
    if 'completed' in data:
        todo.completed = data['completed']
    if 'priority' in data:
        todo.priority = data['priority']
    
    db.session.commit()
    
    return jsonify(todo.to_dict())

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({'error': 'Todo not found'}), 404
    
    db.session.delete(todo)
    db.session.commit()
    
    return jsonify({'message': 'deleted'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)