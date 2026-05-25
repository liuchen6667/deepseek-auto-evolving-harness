# TODO REST API

A simple REST API for managing TODO items built with Flask and SQLite.

## Features

- Full CRUD operations for TODO items
- SQLite database for persistent storage
- Input validation and error handling
- Filtering by completion status
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

**Response**: `200` with JSON array of todo objects

#### GET /todos/<id>
Get a single todo by ID.

**Response**: `200` with todo object, or `404` if not found

#### POST /todos
Create a new todo.

**Request body**: `{"title": "...", "description": "...", "priority": "..."}`

- `title` is required, others optional
- **Response**: `201` with created todo object
- **Error**: `400` if title is missing or empty

#### PUT /todos/<id>
Update an existing todo.

**Request body**: any subset of `{title, description, completed, priority}`

**Response**: `200` with updated todo object
**Error**: `404` if not found

#### DELETE /todos/<id>
Delete a todo.

**Response**: `200` with `{"message": "deleted"}`
**Error**: `404` if not found

### Error Format
```json
{"error": "description of the error"}
```

## Setup and Installation

1. **Clone or download the project**

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## Running the Application

### Development Server
```bash
python app.py
```
The server will start on `http://localhost:5000`

### Using the API

#### Create a todo:
```bash
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries", "description": "Milk, eggs, bread", "priority": "high"}'
```

#### Get all todos:
```bash
curl http://localhost:5000/todos
```

#### Get todos filtered by completion status:
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
  -d '{"title": "Updated title", "completed": true}'
```

#### Delete a todo:
```bash
curl -X DELETE http://localhost:5000/todos/1
```

## Running Tests

The project includes a comprehensive test suite with pytest.

### Install test dependencies:
```bash
pip install pytest
```

### Run all tests:
```bash
python -m pytest test_api.py -v
```

### Run tests with coverage:
```bash
pip install pytest-cov
python -m pytest test_api.py --cov=app --cov-report=term-missing
```

## Project Structure

```
.
├── app.py              # Main Flask application
├── test_api.py         # Test suite with 14+ test cases
├── requirements.txt    # Python dependencies
├── todos.db           # SQLite database (created automatically)
└── README.md          # This file
```

## Database

- Uses SQLite with file `todos.db`
- Database table is created automatically on first run
- For testing, an in-memory database is used

## Testing Details

The test suite includes 14 test cases covering:

1. Successful todo creation
2. Creation with missing title (error)
3. Creation with empty title (error)
4. Getting all todos
5. Getting a specific todo
6. Getting non-existent todo (error)
7. Successful todo update
8. Updating non-existent todo (error)
9. Successful todo deletion
10. Deleting non-existent todo (error)
11. Filtering todos by completion status
12. Creation with invalid priority (error)
13. Partial todo updates
14. Title length validation

To run all tests and ensure they pass:
```bash
python -m pytest test_api.py -v
```