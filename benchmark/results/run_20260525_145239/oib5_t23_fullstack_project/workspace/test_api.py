import pytest
import json
import tempfile
import os
from app import app, init_db, get_db

@pytest.fixture
def client():
    # Use temporary database for tests
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
    os.close(db_fd)
    os.unlink(app.config['DATABASE'])

def test_get_empty_todos(client):
    response = client.get('/todos')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data == []

def test_create_todo_success(client):
    response = client.post('/todos', 
                          json={'title': 'Test todo', 'description': 'Test description', 'priority': 'high'})
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['title'] == 'Test todo'
    assert data['description'] == 'Test description'
    assert data['priority'] == 'high'
    assert data['completed'] is False
    assert 'id' in data
    assert 'created_at' in data

def test_create_todo_missing_title(client):
    response = client.post('/todos', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_create_todo_empty_title(client):
    response = client.post('/todos', json={'title': '   '})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_get_todo_by_id(client):
    # First create a todo
    create_resp = client.post('/todos', json={'title': 'Find me'})
    todo_id = json.loads(create_resp.data)['id']
    
    response = client.get(f'/todos/{todo_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Find me'
    assert data['id'] == todo_id

def test_get_nonexistent_todo(client):
    response = client.get('/todos/9999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

def test_update_todo(client):
    create_resp = client.post('/todos', json={'title': 'Original', 'priority': 'low'})
    todo_id = json.loads(create_resp.data)['id']
    
    response = client.put(f'/todos/{todo_id}', 
                         json={'title': 'Updated', 'completed': True, 'priority': 'high'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['title'] == 'Updated'
    assert data['completed'] is True
    assert data['priority'] == 'high'

def test_update_nonexistent_todo(client):
    response = client.put('/todos/9999', json={'title': 'Test'})
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

def test_delete_todo(client):
    create_resp = client.post('/todos', json={'title': 'To delete'})
    todo_id = json.loads(create_resp.data)['id']
    
    response = client.delete(f'/todos/{todo_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == 'deleted'
    
    # Verify it's gone
    get_resp = client.get(f'/todos/{todo_id}')
    assert get_resp.status_code == 404

def test_delete_nonexistent_todo(client):
    response = client.delete('/todos/9999')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data

def test_filter_by_completed(client):
    # Create completed and incomplete todos
    client.post('/todos', json={'title': 'Todo 1', 'completed': True})
    client.post('/todos', json={'title': 'Todo 2', 'completed': False})
    
    response = client.get('/todos?completed=true')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == 'Todo 1'
    
    response = client.get('/todos?completed=false')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 1
    assert data[0]['title'] == 'Todo 2'

def test_list_all_todos(client):
    client.post('/todos', json={'title': 'Todo A'})
    client.post('/todos', json={'title': 'Todo B'})
    
    response = client.get('/todos')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data) == 2
    titles = [item['title'] for item in data]
    assert 'Todo A' in titles
    assert 'Todo B' in titles
