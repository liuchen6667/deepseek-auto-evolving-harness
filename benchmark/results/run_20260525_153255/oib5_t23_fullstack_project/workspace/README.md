# TODO REST API

A simple REST API for managing TODO items with SQLite storage, built with Flask.

## Features

- Full CRUD operations for TODO items
- SQLite database persistence
- Filtering by completion status
- Input validation
- Comprehensive test suite

## API Specification

See [spec.md](spec.md) for detailed API documentation.

## Getting Started

### Prerequisites

- Python 3.7+
- pip (Python package manager)

### Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the API

```bash
python app.py
```

The API will start at `http://localhost:5000`.

### API Endpoints

- `GET /todos` - List all todos (supports `?completed=true|false` filter)
- `GET /todos/<id>` - Get a single todo
- `POST /todos` - Create a new todo
- `PUT /todos/<id>` - Update a todo
- `DELETE /todos/<id>` - Delete a todo

### Example Usage

```bash
# Create a todo
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "priority": "high"}'

# List all todos
curl http://localhost:5000/todos

# Update a todo
curl -X PUT http://localhost:5000/todos/1 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Delete a todo
curl -X DELETE http://localhost:5000/todos/1
```

## Testing

Run the test suite:

```bash
python -m pytest test_api.py -v
```

Or run the test file directly:

```bash
python test_api.py
```

The test suite includes:
- Creating todos
- Reading todos
- Updating todos
- Deleting todos
- Filtering by completion status
- Error handling for invalid data
- Edge cases

## Project Structure

- `app.py` - Main Flask application
- `test_api.py` - Test suite
- `requirements.txt` - Python dependencies
- `spec.md` - API specification
- `README.md` - This file

## Database

The application uses SQLite with a file named `todos.db`. The database is automatically created when the application starts.

Table schema:
```sql
CREATE TABLE todos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    completed BOOLEAN DEFAULT 0,
    priority TEXT DEFAULT 'medium',
    created_at TEXT NOT NULL
)
```

## Error Handling

All errors return JSON responses with an "error" field:

```json
{"error": "description of the error"}
```

Common error codes:
- `400` - Bad request (invalid input)
- `404` - Not found

## Validation Rules

- Title: Required, 1-200 characters
- Priority: Must be "low", "medium", or "high" (default: "medium")
- Completed: Boolean (default: false)
