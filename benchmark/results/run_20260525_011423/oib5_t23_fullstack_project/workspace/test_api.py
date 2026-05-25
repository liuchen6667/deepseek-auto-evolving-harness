import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, Base, get_db
from datetime import datetime

# Create test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_todos.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Setup and teardown
@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_create_todo_success():
    """Test creating a todo with valid data"""
    response = client.post("/todos", json={
        "title": "Test Todo",
        "description": "Test description",
        "priority": "high"
    })
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "Test description"
    assert data["priority"] == "high"
    assert data["completed"] == False
    assert "id" in data
    assert "created_at" in data

def test_create_todo_missing_title():
    """Test creating a todo without title (should fail)"""
    response = client.post("/todos", json={
        "description": "No title"
    })
    
    assert response.status_code == 422  # Validation error

def test_create_todo_empty_title():
    """Test creating a todo with empty title (should fail)"""
    response = client.post("/todos", json={
        "title": "   ",
        "description": "Empty title"
    })
    
    assert response.status_code == 422  # Validation error

def test_get_todo_by_id():
    """Test retrieving a todo by ID"""
    # First create a todo
    create_response = client.post("/todos", json={
        "title": "Get Test",
        "description": "For get test"
    })
    todo_id = create_response.json()["id"]
    
    # Then retrieve it
    response = client.get(f"/todos/{todo_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Get Test"
    assert data["description"] == "For get test"

def test_get_nonexistent_todo():
    """Test retrieving a todo that doesn't exist"""
    response = client.get("/todos/9999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"

def test_list_todos():
    """Test listing all todos"""
    # Create some todos
    client.post("/todos", json={"title": "Todo 1"})
    client.post("/todos", json={"title": "Todo 2"})
    
    response = client.get("/todos")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Todo 2"  # Most recent first
    assert data[1]["title"] == "Todo 1"

def test_list_todos_filter_completed():
    """Test listing todos with completed filter"""
    # Create todos with different completion status
    todo1 = client.post("/todos", json={"title": "Incomplete"}).json()
    todo2 = client.post("/todos", json={"title": "Complete"}).json()
    
    # Mark second as completed
    client.put(f"/todos/{todo2['id']}", json={"completed": True})
    
    # Test filter for completed
    response = client.get("/todos?completed=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Complete"
    
    # Test filter for incomplete
    response = client.get("/todos?completed=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Incomplete"

def test_update_todo_partial():
    """Test partial update of a todo"""
    # Create a todo
    create_response = client.post("/todos", json={
        "title": "Original Title",
        "description": "Original description",
        "priority": "low"
    })
    todo_id = create_response.json()["id"]
    
    # Update only description
    response = client.put(f"/todos/{todo_id}", json={
        "description": "Updated description"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Original Title"  # Unchanged
    assert data["description"] == "Updated description"
    assert data["priority"] == "low"  # Unchanged

def test_update_todo_full():
    """Test full update of a todo"""
    # Create a todo
    create_response = client.post("/todos", json={
        "title": "Original",
        "description": "Original",
        "priority": "low"
    })
    todo_id = create_response.json()["id"]
    
    # Update all fields
    response = client.put(f"/todos/{todo_id}", json={
        "title": "Updated Title",
        "description": "Updated description",
        "completed": True,
        "priority": "high"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Updated description"
    assert data["completed"] == True
    assert data["priority"] == "high"

def test_update_nonexistent_todo():
    """Test updating a todo that doesn't exist"""
    response = client.put("/todos/9999", json={
        "title": "Updated"
    })
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"

def test_delete_todo():
    """Test deleting a todo"""
    # Create a todo
    create_response = client.post("/todos", json={"title": "To Delete"})
    todo_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(f"/todos/{todo_id}")
    
    assert response.status_code == 200
    assert response.json() == {"message": "deleted"}
    
    # Verify it's gone
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404

def test_delete_nonexistent_todo():
    """Test deleting a todo that doesn't exist"""
    response = client.delete("/todos/9999")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"

def test_priority_validation():
    """Test that priority must be low, medium, or high"""
    response = client.post("/todos", json={
        "title": "Test",
        "priority": "invalid"
    })
    
    assert response.status_code == 422  # Validation error
    
    # Test valid priority
    response = client.post("/todos", json={
        "title": "Test",
        "priority": "medium"
    })
    assert response.status_code == 201

def test_title_length_validation():
    """Test title length validation"""
    # Too long title
    long_title = "a" * 201
    response = client.post("/todos", json={
        "title": long_title
    })
    
    assert response.status_code == 422  # Validation error
    
    # Valid title length
    valid_title = "a" * 200
    response = client.post("/todos", json={
        "title": valid_title
    })
    assert response.status_code == 201

if __name__ == "__main__":
    pytest.main([__file__, "-v"])