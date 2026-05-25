import pytest
import json
import os
from app import app, db, Todo

@pytest.fixture
def client():
    # Use an in-memory database for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
    
    # Cleanup
    with app.app_context():
        db.drop_all()

def test_create_todo_success(client):
    """Test creating a todo with valid data"""
    data = {
        'title': 'Test todo',
        'description': 'Test description',
        'priority': 'high'
    }
    
    response = client.post('/todos', 
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['title'] == 'Test todo'
    assert json_data['description'] == 'Test description'
    assert json_data['priority'] == 'high'
    assert json_data['completed'] == False
    assert 'id' in json_data
    assert 'created_at' in json_data

def test_create_todo_missing_title(client):
    """Test creating a todo without title (should fail)"""
    data = {
        'description': 'Test description'
    }
    
    response = client.post('/todos',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'title is required' in json_data['error']

def test_create_todo_empty_title(client):
    """Test creating a todo with empty title (should fail)"""
    data = {
        'title': '',
        'description': 'Test description'
    }
    
    response = client.post('/todos',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'title cannot be empty' in json_data['error']

def test_get_all_todos(client):
    """Test getting all todos"""
    # Create some test todos
    with app.app_context():
        todo1 = Todo(title='Todo 1', description='Desc 1', priority='high')
        todo2 = Todo(title='Todo 2', description='Desc 2', priority='low', completed=True)
        db.session.add(todo1)
        db.session.add(todo2)
        db.session.commit()
    
    response = client.get('/todos')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 2
    assert json_data[0]['title'] == 'Todo 1'
    assert json_data[1]['title'] == 'Todo 2'

def test_get_todo_by_id(client):
    """Test getting a specific todo by ID"""
    with app.app_context():
        todo = Todo(title='Test todo', description='Test desc')
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    
    response = client.get(f'/todos/{todo_id}')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['title'] == 'Test todo'
    assert json_data['description'] == 'Test desc'
    assert json_data['id'] == todo_id

def test_get_nonexistent_todo(client):
    """Test getting a todo that doesn't exist"""
    response = client.get('/todos/999')
    
    assert response.status_code == 404
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'Todo not found' in json_data['error']

def test_update_todo_success(client):
    """Test updating a todo successfully"""
    with app.app_context():
        todo = Todo(title='Original title', description='Original desc', priority='medium')
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    
    update_data = {
        'title': 'Updated title',
        'description': 'Updated description',
        'completed': True,
        'priority': 'high'
    }
    
    response = client.put(f'/todos/{todo_id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['title'] == 'Updated title'
    assert json_data['description'] == 'Updated description'
    assert json_data['completed'] == True
    assert json_data['priority'] == 'high'

def test_update_nonexistent_todo(client):
    """Test updating a todo that doesn't exist"""
    update_data = {'title': 'New title'}
    
    response = client.put('/todos/999',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 404
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'Todo not found' in json_data['error']

def test_delete_todo_success(client):
    """Test deleting a todo successfully"""
    with app.app_context():
        todo = Todo(title='To be deleted', description='Will be gone')
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    
    response = client.delete(f'/todos/{todo_id}')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['message'] == 'deleted'
    
    # Verify it's actually deleted
    with app.app_context():
        deleted_todo = Todo.query.get(todo_id)
        assert deleted_todo is None

def test_delete_nonexistent_todo(client):
    """Test deleting a todo that doesn't exist"""
    response = client.delete('/todos/999')
    
    assert response.status_code == 404
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'Todo not found' in json_data['error']

def test_filter_todos_by_completed(client):
    """Test filtering todos by completed status"""
    with app.app_context():
        todo1 = Todo(title='Incomplete', completed=False)
        todo2 = Todo(title='Complete', completed=True)
        todo3 = Todo(title='Another incomplete', completed=False)
        db.session.add_all([todo1, todo2, todo3])
        db.session.commit()
    
    # Get only completed todos
    response = client.get('/todos?completed=true')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 1
    assert json_data[0]['title'] == 'Complete'
    assert json_data[0]['completed'] == True
    
    # Get only incomplete todos
    response = client.get('/todos?completed=false')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 2
    for todo in json_data:
        assert todo['completed'] == False

def test_create_todo_with_invalid_priority(client):
    """Test creating a todo with invalid priority value"""
    data = {
        'title': 'Test todo',
        'priority': 'invalid'
    }
    
    response = client.post('/todos',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'priority must be one of: low, medium, high' in json_data['error']

def test_update_todo_partial(client):
    """Test updating only some fields of a todo"""
    with app.app_context():
        todo = Todo(title='Original', description='Original desc', priority='low', completed=False)
        db.session.add(todo)
        db.session.commit()
        todo_id = todo.id
    
    # Update only title and completed status
    update_data = {
        'title': 'New title',
        'completed': True
    }
    
    response = client.put(f'/todos/{todo_id}',
                         data=json.dumps(update_data),
                         content_type='application/json')
    
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['title'] == 'New title'
    assert json_data['completed'] == True
    assert json_data['description'] == 'Original desc'  # Should remain unchanged
    assert json_data['priority'] == 'low'  # Should remain unchanged

def test_title_length_validation(client):
    """Test that title length validation works"""
    # Test title too long
    data = {
        'title': 'a' * 201,  # 201 characters
        'description': 'Test'
    }
    
    response = client.post('/todos',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert 'title must be 200 characters or less' in json_data['error']
    
    # Test title at max length (should succeed)
    data['title'] = 'a' * 200  # 200 characters
    
    response = client.post('/todos',
                          data=json.dumps(data),
                          content_type='application/json')
    
    assert response.status_code == 201

if __name__ == '__main__':
    # Run tests directly if needed
    pytest.main(['-v', __file__])