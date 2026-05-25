# TODO REST API

A simple REST API for managing TODO items with SQLite storage, built with Flask.

## Features

- Full CRUD operations for TODO items
- SQLite database for persistence
- Filtering by completion status
- Input validation
- Comprehensive test suite

## API Specification

### Data Model

| Field       | Type    | Required | Description                    |
|-------------|---------|----------|--------------------------------|
| id          | integer | auto     | Auto-increment primary key     |
| title       | string  | yes      | Todo title (1-200 chars)       |
| description | string  | no       | Optional description           |
| completed   | boolean | no       | Default: false                 |
| priority    | string  | no       | "low", "medium", "high". Default: "medium" |
| created_at  | string  | auto     | ISO 8601 timestamp             |

### Endpoints

#### GET /todos
List all todos. Supports query parameter `?completed=true|false` for filtering.
- Response: `200` with JSON array of todo objects

#### GET /todos/<id>
Get a single todo by ID.
- Response: `200` with todo object, or `404` if not found

#### POST /todos
Create a new todo.
- Request body: `{"title": "...", "description": "...", "priority": "..."}`
- `title` is required, others optional
- Response: `201` with created todo object
- Error: `400` if title is missing or empty

#### PUT /todos/<id>
Update an existing todo.
- Request body: any subset of `{title, description, completed, priority}`
- Response: `200` with updated todo object
- Error: `404` if not found

#### DELETE /todos/<id>
Delete a todo.
- Response: `200` with `{"message": "deleted"}`
- Error: `404` if not found

### Error Format
```json
{"error": "description of the error"}
```

## Setup and Installation

### Prerequisites
- Python 3.6+

### Installation

1. Clone or download the project files.

2. Install required dependencies:
```bash
pip install flask
```

If you want to run tests:
```bash
pip install pytest
```

## Running the API

### Development Server
Run the Flask development server:
```bash
python app.py
```

The server will start on `http://localhost:5000`.

The database (`todos.db`) will be created automatically on first run.

### Using the API

#### Create a todo:
```bash
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "priority": "high"}'
```

#### Get all todos:
```bash
curl http://localhost:5000/todos
```

#### Get filtered todos (completed=false):
```bash
curl "http://localhost:5000/todos?completed=false"
```

#### Get a specific todo:
```bash
curl http://localhost:5000/todos/1
```

#### Update a todo:
```bash
curl -X PUT http://localhost:5000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true, "priority": "low"}'
```

#### Delete a todo:
```bash
curl -X DELETE http://localhost:5000/todos/1
```

## Running Tests

Run the test suite with pytest:
```bash
pytest test_api.py -v
```

Or run the tests directly:
```bash
python test_api.py
```

The test suite includes 10 test cases covering:
- Listing all todos with and without filters
- Getting individual todos
- Creating todos with validation
- Updating todos (full and partial updates)
- Deleting todos
- Error handling
- Default values
- Empty database scenarios

## Project Structure

- `app.py` - Main Flask application with all API endpoints
- `test_api.py` - Comprehensive test suite
- `todos.db` - SQLite database (created automatically)
- `README.md` - This documentation file

## Database Schema

The SQLite database uses the following schema:
```sql
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL CHECK(length(title) <= 200),
    description TEXT,
    completed BOOLEAN DEFAULT 0,
    priority TEXT CHECK(priority IN ('low', 'medium', 'high')) DEFAULT 'medium',
    created_at TEXT DEFAULT (datetime('now'))
);
```

## Notes

- The API automatically creates the database table on first run
- All timestamps are in ISO 8601 format
- Input validation ensures data integrity
- The test suite uses a separate test database to avoid interfering with production data
