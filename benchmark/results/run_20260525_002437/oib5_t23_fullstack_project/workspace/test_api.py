import pytest
import json
import sqlite3
import os
from datetime import datetime
from app import app

# Test database path
TEST_DB = 'test_todos.db'

@pytest.fixture
def client():
    """Create a test client for the app."""
    # Use a test database
    app.config['TESTING'] = True
    app.config['DATABASE'] = TEST_DB
    
    with app.test_client() as client:
        with app.app_context():
            # Initialize test database
            conn = sqlite3.connect(TEST_DB)
            cursor = conn.cursor()
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
            conn.commit()
            conn.close()
        
        yield client
    
    # Clean up test database after tests
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def setup_test_db():
    """Helper to set up test database with initial data."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    conn = sqlite3.connect(TEST_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL CHECK(length(title) <= 200),
            description TEXT,
            completed BOOLEAN DEFAULT 0,
            priority TEXT CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')
    
    # Insert some test data
    test_todos = [
        ('Buy groceries', 'Milk, eggs, bread', 0, 'high'),
        ('Finish project', 'Complete the API implementation', 1, 'medium'),
        ('Call mom', 'Wish her happy birthday', 0, 'low'),
        ('Exercise', 'Go for a run', 0, 'medium'),
    ]
    
    for todo in test_todos:
        cursor.execute(
            'INSERT INTO todos (title, description, completed, priority) VALUES (?, ?, ?, ?)',
            todo
        )
    
    conn.commit()
    conn.close()

# Test 1: GET /todos - List all todos
def test_get_all_todos(client):
    setup_test_db()
    
    response = client.get('/todos')
    assert response.status_code == 200
    
    todos = json.loads(response.data)
    assert len(todos) == 4
    assert todos[0]['title'] == 'Buy groceries'
    assert todos[1]['title'] == 'Finish project'
    assert todos[1]['completed'] == True

# Test 2: GET /todos with completed filter
def test_get_todos_filtered(client):
    setup_test_db()
    
    # Filter by completed=true
    response = client.get('/todos?completed=true')
    assert response.status_code == 200
    todos = json.loads(response.data)
    assert len(todos) == 1
    assert todos[0]['title'] == 'Finish project'
    assert todos[0]['completed'] == True
    
    # Filter by completed=false
    response = client.get('/todos?completed=false')
    assert response.status_code == 200
    todos = json.loads(response.data)
    assert len(todos) == 3
    
    # Invalid filter value
    response = client.get('/todos?completed=invalid')
    assert response.status_code == 400

# Test 3: GET /todos/<id> - Get single todo
def test_get_single_todo(client):
    setup_test_db()
    
    # Get existing todo
    response = client.get('/todos/1')
    assert response.status_code == 200
    todo = json.loads(response.data)
    assert todo['id'] == 1
    assert todo['title'] == 'Buy groceries'
    assert todo['priority'] == 'high'
    
    # Get non-existent todo
    response = client.get('/todos/999')
    assert response.status_code == 404
    error = json.loads(response.data)
    assert 'error' in error

# Test 4: POST /todos - Create new todo
def test_create_todo(client):
    setup_test_db()
    
    # Create valid todo
    new_todo = {
        'title': 'Test todo',
        'description': 'Test description',
        'priority': 'low'
    }
    
    response = client.post('/todos', 
                          data=json.dumps(new_todo),
                          content_type='application/json')
    
    assert response.status_code == 201
    created_todo = json.loads(response.data)
    assert created_todo['title'] == 'Test todo'
    assert created_todo['description'] == 'Test description'
    assert created_todo['priority'] == 'low'
    assert created_todo['completed'] == False
    assert 'id' in created_todo
    assert 'created_at' in created_todo
    
    # Verify it was added to the database
    response = client.get('/todos')
    todos = json.loads(response.data)
    assert len(todos) == 5

# Test 5: POST /todos - Validation errors
def test_create_todo_validation(client):
    setup_test_db()
    
    # Missing title
    response = client.post('/todos',
                          data=json.dumps({'description': 'No title'}),
                          content_type='application/json')
    assert response.status_code == 400
    
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

# Test 6: PUT /todos/<id> - Update todo
def test_update_todo(client):
    setup_test_db()
    
    # Update existing todo
    updates = {
        'title': 'Updated title',
        'description': 'Updated description',
        'completed': True,
        'priority': 'low'
    }
    
    response = client.put('/todos/1',
                         data=json.dumps(updates),
                         content_type='application/json')
    
    assert response.status_code == 200
    updated_todo = json.loads(response.data)
    assert updated_todo['title'] == 'Updated title'
    assert updated_todo['description'] == 'Updated description'
    assert updated_todo['completed'] == True
    assert updated_todo['priority'] == 'low'
    
    # Verify partial update
    partial_update = {'completed': False}
    response = client.put('/todos/2',
                         data=json.dumps(partial_update),
                         content_type='application/json')
    
    assert response.status_code == 200
    updated_todo = json.loads(response.data)
    assert updated_todo['completed'] == False
    # Other fields should remain unchanged
    assert updated_todo['title'] == 'Finish project'

# Test 7: PUT /todos/<id> - Error cases
def test_update_todo_errors(client):
    setup_test_db()
    
    # Update non-existent todo
    response = client.put('/todos/999',
                         data=json.dumps({'title': 'New title'}),
                         content_type='application/json')
    assert response.status_code == 404
    
    # Update with empty title
    response = client.put('/todos/1',
                         data=json.dumps({'title': ''}),
                         content_type='application/json')
    assert response.status_code == 400
    
    # Update with invalid priority
    response = client.put('/todos/1',
                         data=json.dumps({'priority': 'invalid'}),
                         content_type='application/json')
    assert response.status_code == 400
    
    # Update with invalid completed type
    response = client.put('/todos/1',
                         data=json.dumps({'completed': 'not-a-boolean'}),
                         content_type='application/json')
    assert response.status_code == 400

# Test 8: DELETE /todos/<id> - Delete todo
def test_delete_todo(client):
    setup_test_db()
    
    # Delete existing todo
    response = client.delete('/todos/1')
    assert response.status_code == 200
    result = json.loads(response.data)
    assert result['message'] == 'deleted'
    
    # Verify it was deleted
    response = client.get('/todos/1')
    assert response.status_code == 404
    
    # Delete non-existent todo
    response = client.delete('/todos/999')
    assert response.status_code == 404

# Test 9: Additional test - Check default values
def test_default_values(client):
    setup_test_db()
    
    # Create todo with only title
    new_todo = {'title': 'Minimal todo'}
    
    response = client.post('/todos',
                          data=json.dumps(new_todo),
                          content_type='application/json')
    
    assert response.status_code == 201
    created_todo = json.loads(response.data)
    assert created_todo['completed'] == False
    assert created_todo['priority'] == 'medium'  # default
    assert created_todo['description'] == ''  # default empty string
    
    # Check created_at is present and valid ISO format
    try:
        datetime.fromisoformat(created_todo['created_at'].replace('Z', '+00:00'))
        assert True
    except ValueError:
        assert False, "created_at is not valid ISO format"

# Test 10: Additional test - Empty database
def test_empty_database(client):
    # Start with empty database
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    
    # GET all todos from empty database
    response = client.get('/todos')
    assert response.status_code == 200
    todos = json.loads(response.data)
    assert len(todos) == 0
    
    # Filter on empty database
    response = client.get('/todos?completed=true')
    assert response.status_code == 200
    todos = json.loads(response.data)
    assert len(todos) == 0

if __name__ == '__main__':
    # Run tests directly if needed
    pytest.main(['-v', __file__])
