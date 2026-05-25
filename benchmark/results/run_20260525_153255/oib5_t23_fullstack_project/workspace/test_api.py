import pytest
import json
import os
import tempfile
import sys
from app import app

@pytest.fixture
def client():
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    app.config['DATABASE'] = db_path
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            # Initialize database
            import sqlite3
            conn = sqlite3.connect(db_path)
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
            conn.close()
        yield client
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)

def test_get_empty_todos(client):
    """Test GET /todos with empty database"""
    response = client.get('/todos')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []

def test_create_todo(client):
    """Test POST /todos to create a new todo"""
    todo_data = {
        'title': 'Test Todo',
        'description': 'This is a test todo',
        'priority': 'high'
    }
    
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test Todo'
    assert data['description'] == 'This is a test todo'
    assert data['priority'] == 'high'
    assert data['completed'] == False
    assert 'id' in data
    assert 'created_at' in data
    
    # Verify it appears in the list
    response = client.get('/todos')
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == 'Test Todo'

def test_get_todo_by_id(client):
    """Test GET /todos/<id> to get a single todo"""
    # First create a todo
    todo_data = {'title': 'Get by ID test'}
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    created_todo = json.loads(response.data)
    todo_id = created_todo['id']
    
    # Now get it by ID
    response = client.get(f'/todos/{todo_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == todo_id
    assert data['title'] == 'Get by ID test'

def test_get_nonexistent_todo(client):
    """Test GET /todos/<id> with non-existent ID"""
    response = client.get('/todos/9999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Todo not found'

def test_update_todo(client):
    """Test PUT /todos/<id> to update a todo"""
    # First create a todo
    todo_data = {'title': 'Original title'}
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    created_todo = json.loads(response.data)
    todo_id = created_todo['id']
    
    # Update it
    update_data = {
        'title': 'Updated title',
        'description': 'Updated description',
        'completed': True,
        'priority': 'low'
    }
    
    response = client.put(f'/todos/{todo_id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Updated title'
    assert data['description'] == 'Updated description'
    assert data['completed'] == True
    assert data['priority'] == 'low'
    assert data['id'] == todo_id
    
    # Verify update persisted
    response = client.get(f'/todos/{todo_id}')
    data = json.loads(response.data)
    assert data['title'] == 'Updated title'

def test_delete_todo(client):
    """Test DELETE /todos/<id> to delete a todo"""
    # First create a todo
    todo_data = {'title': 'To be deleted'}
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    created_todo = json.loads(response.data)
    todo_id = created_todo['id']
    
    # Delete it
    response = client.delete(f'/todos/{todo_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'deleted'
    
    # Verify it's gone
    response = client.get(f'/todos/{todo_id}')
    assert response.status_code == 404
    
    # Verify it's not in the list
    response = client.get('/todos')
    data = json.loads(response.data)
    assert len(data) == 0

def test_filter_todos_by_completed(client):
    """Test GET /todos?completed=true|false for filtering"""
    # Create completed todo
    client.post('/todos', 
               data=json.dumps({'title': 'Completed todo', 'completed': True}),
               content_type='application/json')
    
    # Create incomplete todo
    client.post('/todos', 
               data=json.dumps({'title': 'Incomplete todo', 'completed': False}),
               content_type='application/json')
    
    # Test completed filter
    response = client.get('/todos?completed=true')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == 'Completed todo'
    assert data[0]['completed'] == True
    
    # Test incomplete filter
    response = client.get('/todos?completed=false')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == 'Incomplete todo'
    assert data[0]['completed'] == False
    
    # Test invalid filter value
    response = client.get('/todos?completed=invalid')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_create_todo_invalid_data(client):
    """Test POST /todos with invalid data"""
    # Missing title
    response = client.post('/todos',
                          data=json.dumps({'description': 'No title'}),
                          content_type='application/json')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    
    # Empty title
    response = client.post('/todos',
                          data=json.dumps({'title': ''}),
                          content_type='application/json')
    assert response.status_code == 400
    
    # Title too long
    long_title = 'x' * 201
    response = client.post('/todos',
                          data=json.dumps({'title': long_title}),
                          content_type='application/json')
    assert response.status_code == 400
    
    # Invalid priority
    response = client.post('/todos',
                          data=json.dumps({'title': 'Test', 'priority': 'invalid'}),
                          content_type='application/json')
    assert response.status_code == 400

def test_update_todo_invalid_data(client):
    """Test PUT /todos/<id> with invalid data"""
    # First create a todo
    todo_data = {'title': 'Test todo'}
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    created_todo = json.loads(response.data)
    todo_id = created_todo['id']
    
    # Empty title
    response = client.put(f'/todos/{todo_id}',
                         data=json.dumps({'title': ''}),
                         content_type='application/json')
    assert response.status_code == 400
    
    # Invalid priority
    response = client.put(f'/todos/{todo_id}',
                         data=json.dumps({'priority': 'invalid'}),
                         content_type='application/json')
    assert response.status_code == 400
    
    # Invalid completed type
    response = client.put(f'/todos/{todo_id}',
                         data=json.dumps({'completed': 'not-a-bool'}),
                         content_type='application/json')
    assert response.status_code == 400
    
    # No data provided
    response = client.put(f'/todos/{todo_id}',
                         data=json.dumps({}),
                         content_type='application/json')
    assert response.status_code == 400

def test_delete_nonexistent_todo(client):
    """Test DELETE /todos/<id> with non-existent ID"""
    response = client.delete('/todos/9999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert data['error'] == 'Todo not found'

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
