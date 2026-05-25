# TODO REST API

A simple REST API for managing TODO items with SQLite storage, built with FastAPI.

## Features

- Full CRUD operations for TODO items
- SQLite database persistence
- Input validation (title length, priority values)
- Filtering by completion status
- Automatic timestamp generation
- Comprehensive test suite

## API Specification

See [spec.md](spec.md) for detailed API specification.

## Setup and Installation

1. **Clone or download the project**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the API

### Development server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### GET /todos
List all todos. Optional query parameter: `?completed=true|false`

**Response:** `200 OK` with JSON array of todo objects

### GET /todos/{id}
Get a single todo by ID.

**Response:** `200 OK` with todo object, or `404 Not Found`

### POST /todos
Create a new todo.

**Request body:**
```json
{
  "title": "string (required, 1-200 chars)",
  "description": "string (optional)",
  "priority": "low|medium|high (optional, default: medium)"
}
```

**Response:** `201 Created` with created todo object

### PUT /todos/{id}
Update an existing todo.

**Request body:** Any subset of fields to update
```json
{
  "title": "string (optional)",
  "description": "string (optional)",
  "completed": "boolean (optional)",
  "priority": "low|medium|high (optional)"
}
```

**Response:** `200 OK` with updated todo object, or `404 Not Found`

### DELETE /todos/{id}
Delete a todo.

**Response:** `200 OK` with `{"message": "deleted"}`, or `404 Not Found`

## Data Model

| Field       | Type    | Required | Description                    |
|-------------|---------|----------|--------------------------------|
| id          | integer | auto     | Auto-increment primary key     |
| title       | string  | yes      | Todo title (1-200 chars)       |
| description | string  | no       | Optional description           |
| completed   | boolean | no       | Default: false                 |
| priority    | string  | no       | "low", "medium", "high". Default: "medium" |
| created_at  | string  | auto     | ISO 8601 timestamp             |

## Error Format

```json
{
  "detail": "description of the error"
}
```

## Running Tests

The project includes a comprehensive test suite with 14 test cases.

### Run all tests:
```bash
pytest test_api.py -v
```

### Run specific test:
```bash
pytest test_api.py::test_create_todo_success -v
```

### Test coverage:
The test suite covers:
- Creating todos with valid and invalid data
- Retrieving todos by ID
- Listing todos with and without filters
- Updating todos (partial and full updates)
- Deleting todos
- Input validation (title length, priority values)
- Error handling for non-existent todos

## Database

- Uses SQLite with file `todos.db`
- Database and table are created automatically on first run
- Test suite uses a separate `test_todos.db` database

## Example Usage

### Create a todo:
```bash
curl -X POST "http://localhost:8000/todos" \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "priority": "high"}'
```

### List all todos:
```bash
curl "http://localhost:8000/todos"
```

### List only completed todos:
```bash
curl "http://localhost:8000/todos?completed=true"
```

### Update a todo:
```bash
curl -X PUT "http://localhost:8000/todos/1" \
  -H "Content-Type: application/json" \
  -d '{"completed": true, "description": "Done!"}'
```

### Delete a todo:
```bash
curl -X DELETE "http://localhost:8000/todos/1"
```

## Project Structure

```
.
├── main.py              # FastAPI application
├── test_api.py          # Test suite (14 test cases)
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── spec.md             # API specification
```

## Dependencies

- FastAPI: Web framework
- SQLAlchemy: ORM for database
- Pydantic: Data validation
- Uvicorn: ASGI server
- Pytest: Testing framework
- HTTPX: HTTP client for tests