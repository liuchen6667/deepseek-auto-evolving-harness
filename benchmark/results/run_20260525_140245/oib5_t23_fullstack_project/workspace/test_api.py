import pytest
import json
import sqlite3
import os
from datetime import datetime
from app import app, init_db, DATABASE

@pytest.fixture
def client():
    """Create a test client"""
    # Use a test database
    global DATABASE
    original_db = DATABASE
    DATABASE = 'test_todos.db'
    
    # Remove test database if exists
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    # Initialize test database
    init_db()
    
    # Set up Flask test client
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client
    
    # Clean up
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    # Restore original database
    DATABASE = original_db

def test_get_empty_todos(client):
    """Test getting todos when database is empty"""
    response = client.get('/todos')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []

def test_create_todo_success(client):
    """Test creating a todo with minimal data"""
    todo_data = {
        'title': 'Test Todo',
        'description': 'Test description',
        'priority': 'high'
    }
    
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    
    assert data['title'] == 'Test Todo'
    assert data['description'] == 'Test description'
    assert data['priority'] == 'high'
    assert data['completed'] == False
    assert 'id' in data
    assert 'created_at' in data

def test_create_todo_missing_title(client):
    """Test creating a todo without title"""
    todo_data = {
        'description': 'Test description'
    }
    
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Title is required' in data['error']

def test_create_todo_empty_title(client):
    """Test creating a todo with empty title"""
    todo_data = {
        'title': '   ',
        'description': 'Test description'
    }
    
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Title cannot be empty' in data['error']

def test_create_todo_title_too_long(client):
    """Test creating a todo with title exceeding 200 characters"""
    todo_data = {
        'title': 'A' * 201,
        'description': 'Test description'
    }
    
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert '200 characters' in data['error'].lower()

def test_get_todo_by_id(client):
    """Test getting a specific todo by ID"""
    # First create a todo
    todo_data = {'title': 'Test Todo'}
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    created_todo = json.loads(response.data)
    todo_id = created_todo['id']
    
    # Then get it by ID
    response = client.get(f'/todos/{todo_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['id'] == todo_id
    assert data['title'] == 'Test Todo'

def test_get_nonexistent_todo(client):
    """Test getting a todo that doesn't exist"""
    response = client.get('/todos/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'not found' in data['error'].lower()

def test_get_todos_with_filter(client):
    """Test getting todos with completed filter"""
    # Create completed and incomplete todos
    todo1 = {'title': 'Todo 1', 'completed': True}
    todo2 = {'title': 'Todo 2', 'completed': False}
    
    client.post('/todos', data=json.dumps(todo1), content_type='application/json')
    client.post('/todos', data=json.dumps(todo2), content_type='application/json')
    
    # Test completed=true filter
    response = client.get('/todos?completed=true')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == 'Todo 1'
    assert data[0]['completed'] == True
    
    # Test completed=false filter
    response = client.get('/todos?completed=false')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == 'Todo 2'
    assert data[0]['completed'] == False

def test_update_todo_success(client):
    """Test updating a todo successfully"""
    # First create a todo
    todo_data = {'title': 'Original Title', 'priority': 'low'}
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    created_todo = json.loads(response.data)
    todo_id = created_todo['id']
    
    # Update the todo
    update_data = {
        'title': 'Updated Title',
        'description': 'Updated description',
        'completed': True,
        'priority': 'high'
    }
    
    response = client.put(f'/todos/{todo_id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['title'] == 'Updated Title'
    assert data['description'] == 'Updated description'
    assert data['completed'] == True
    assert data['priority'] == 'high'
    assert data['id'] == todo_id

def test_update_nonexistent_todo(client):
    """Test updating a todo that doesn't exist"""
    update_data = {'title': 'Updated Title'}
    
    response = client.put('/todos/999',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'not found' in data['error'].lower()

def test_update_todo_empty_title(client):
    """Test updating a todo with empty title"""
    # First create a todo
    todo_data = {'title': 'Original Title'}
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    created_todo = json.loads(response.data)
    todo_id = created_todo['id']
    
    # Try to update with empty title
    update_data = {'title': '   '}
    
    response = client.put(f'/todos/{todo_id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Title cannot be empty' in data['error']

def test_update_todo_invalid_priority(client):
    """Test updating a todo with invalid priority"""
    # First create a todo
    todo_data = {'title': 'Original Title'}
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    created_todo = json.loads(response.data)
    todo_id = created_todo['id']
    
    # Try to update with invalid priority
    update_data = {'priority': 'invalid'}
    
    response = client.put(f'/todos/{todo_id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'priority' in data['error'].lower()

def test_delete_todo_success(client):
    """Test deleting a todo successfully"""
    # First create a todo
    todo_data = {'title': 'Todo to delete'}
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    created_todo = json.loads(response.data)
    todo_id = created_todo['id']
    
    # Delete the todo
    response = client.delete(f'/todos/{todo_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'deleted'
    
    # Verify it's deleted
    response = client.get(f'/todos/{todo_id}')
    assert response.status_code == 404

def test_delete_nonexistent_todo(client):
    """Test deleting a todo that doesn't exist"""
    response = client.delete('/todos/999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'not found' in data['error'].lower()

def test_create_todo_default_values(client):
    """Test creating a todo with default values"""
    todo_data = {'title': 'Test Todo'}
    
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    
    assert data['title'] == 'Test Todo'
    assert data['completed'] == False
    assert data['priority'] == 'medium'
    assert data['description'] == ''
    assert 'id' in data
    assert 'created_at' in data

def test_create_todo_invalid_priority(client):
    """Test creating a todo with invalid priority (should default to medium)"""
    todo_data = {
        'title': 'Test Todo',
        'priority': 'invalid'
    }
    
    response = client.post('/todos', 
                          data=json.dumps(todo_data),
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    
    # Should default to medium
    assert data['priority'] == 'medium'

def test_filter_invalid_completed_param(client):
    """Test filtering with invalid completed parameter"""
    response = client.get('/todos?completed=invalid')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'must be "true" or "false"' in data['error']

if __name__ == '__main__':
    # Run tests directly
    import sys
    sys.exit(pytest.main(['-v', __file__]))
