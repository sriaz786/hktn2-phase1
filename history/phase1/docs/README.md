# Evolution of Todo API

A powerful todo management system with AI-powered assistance and MCP (Model Context Protocol) integration.

## Status: Phase 1

This is Phase 1 of the Evolution of Todo project, providing a backend-only implementation with:
- Complete CRUD operations for todo items
- AI-powered task suggestions, prioritization, and breakdown
- MCP server integration for external tool connectivity
- RESTful API with comprehensive documentation

## Features

- **Todo Management**: Create, read, update, and delete todos with rich metadata
- **Status Tracking**: Track todo status (pending, in_progress, completed, cancelled)
- **Priority Levels**: Set priority levels (low, medium, high, urgent)
- **Filtering & Sorting**: Filter by status, priority, tags and sort by multiple fields
- **AI Assistance**:
  - Generate todo suggestions from natural language
  - Get AI-powered prioritization recommendations
  - Break down complex tasks into manageable subtasks
- **MCP Integration**: External tool connectivity via Model Context Protocol
- **Comprehensive Testing**: 80%+ test coverage with unit and integration tests

## Technology Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Database ORM**: SQLModel
- **Database**: Neon DB (PostgreSQL)
- **AI**: OpenAI API
- **MCP**: Model Context Protocol

## Prerequisites

- Python 3.11 or higher
- Neon DB account and database URL
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd hktn2phase1
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create environment file:
```bash
cp .env.example .env
```

5. Configure your environment variables in `.env`:
```env
DATABASE_URL=postgresql://user:password@ep-xxx.us-east-2.aws.neon.tech/dbname
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-4
API_HOST=0.0.0.0
API_PORT=8000
MCP_ENABLED=true
LOG_LEVEL=INFO
```

## Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Documentation

### Health Check
- `GET /health` - Health check endpoint

### Todo Endpoints
- `POST /api/v1/todos` - Create a new todo
- `GET /api/v1/todos` - List all todos (with filters and sorting)
- `GET /api/v1/todos/{id}` - Get a specific todo
- `PATCH /api/v1/todos/{id}` - Update a todo (partial update)
- `DELETE /api/v1/todos/{id}` - Delete a todo (soft delete)

### AI Endpoints
- `POST /api/v1/ai/suggest` - Generate AI-powered todo suggestions
- `POST /api/v1/ai/prioritize` - Get AI prioritization recommendations
- `POST /api/v1/ai/breakdown` - Break down complex tasks into subtasks

### Query Parameters

**List Todos:**
- `status`: Filter by status (pending, in_progress, completed, cancelled)
- `priority`: Filter by priority (low, medium, high, urgent)
- `tags`: Filter by tags (comma-separated)
- `sort_by`: Sort field (created_at, modified_at, due_date, priority)
- `sort_order`: Sort order (asc, desc)

## Usage Examples

### Create a Todo

```bash
curl -X POST http://localhost:8000/api/v1/todos \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for Phase 1",
    "due_date": "2025-01-10T00:00:00Z",
    "priority": "high",
    "tags": ["documentation", "phase1"]
  }'
```

### List Todos

```bash
# Get all todos
curl http://localhost:8000/api/v1/todos

# Filter by status
curl "http://localhost:8000/api/v1/todos?status=pending"

# Filter and sort
curl "http://localhost:8000/api/v1/todos?priority=high&sort_by=due_date&sort_order=asc"
```

### Update a Todo

```bash
curl -X PATCH http://localhost:8000/api/v1/todos/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress",
    "priority": "urgent"
  }'
```

### Generate AI Suggestions

```bash
curl -X POST http://localhost:8000/api/v1/ai/suggest \
  -H "Content-Type: application/json" \
  -d '{
    "description": "I need to organize my project files and create documentation"
  }'
```

### Get AI Prioritization

```bash
curl -X POST http://localhost:8000/api/v1/ai/prioritize \
  -H "Content-Type: application/json" \
  -d '{
    "todos": [
      {
        "id": 1,
        "title": "Fix critical bug",
        "due_date": "2025-01-07T00:00:00Z",
        "priority": "high"
      },
      {
        "id": 2,
        "title": "Complete documentation",
        "due_date": "2025-01-10T00:00:00Z",
        "priority": "medium"
      }
    ]
  }'
```

### Break Down a Task

```bash
curl -X POST http://localhost:8000/api/v1/ai/breakdown \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Build a complete REST API with authentication and testing"
  }'
```

## Testing

Run all tests:

```bash
pytest
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=html
```

Run specific test file:

```bash
pytest tests/test_todos.py
```

## Code Quality

Format code with Black:

```bash
black app tests
```

Lint code with Ruff:

```bash
ruff check app tests
```

Fix linting issues:

```bash
ruff check --fix app tests
```

Type checking with MyPy:

```bash
mypy app
```

## Project Structure

```
hktn2phase1/
├── app/
│   ├── api/v1/          # API endpoints
│   │   ├── todos.py     # Todo CRUD endpoints
│   │   └── ai.py       # AI endpoints
│   ├── models/          # Data models
│   │   ├── todo.py      # SQLModel entities
│   │   └── schemas.py   # Pydantic schemas
│   ├── services/        # Business logic
│   │   ├── todo_service.py      # Todo business logic
│   │   ├── ai_service.py        # OpenAI integration
│   │   └── mcp_service.py      # MCP server
│   ├── repository/      # Data access
│   │   └── todo_repository.py  # Database operations
│   ├── mcp/            # MCP tools
│   │   └── tools.py    # Tool definitions
│   ├── config.py        # Configuration management
│   ├── database.py      # Database session
│   └── main.py         # FastAPI application
├── tests/
│   ├── test_todos.py          # Todo unit tests
│   ├── test_ai_service.py    # AI service tests
│   ├── test_mcp_service.py   # MCP service tests
│   └── test_integration/     # Integration tests
├── .env.example             # Environment template
├── pyproject.toml           # Project configuration
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Configuration

| Variable | Description | Default | Required |
|----------|-------------|----------|----------|
| DATABASE_URL | PostgreSQL connection string | - | Yes |
| OPENAI_API_KEY | OpenAI API key | - | Yes |
| OPENAI_MODEL | OpenAI model name | gpt-4 | No |
| API_HOST | API host address | 0.0.0.0 | No |
| API_PORT | API port | 8000 | No |
| MCP_ENABLED | Enable MCP server | true | No |
| MCP_PORT | MCP server port | 3000 | No |
| LOG_LEVEL | Logging level | INFO | No |

## Data Model

### Todo Entity

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | auto-generated | Unique identifier |
| title | string | yes | Todo title (1-200 chars) |
| description | string | no | Description (max 2000 chars) |
| due_date | datetime | no | Due date |
| priority | enum | no | low, medium, high, urgent (default: medium) |
| status | enum | no | pending, in_progress, completed, cancelled (default: pending) |
| tags | array | no | List of tags |
| created_at | datetime | auto-generated | Creation timestamp |
| modified_at | datetime | auto-generated | Last modification timestamp |
| is_deleted | boolean | no | Soft delete flag |

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {}
  }
}
```

Error codes:
- `VALIDATION_ERROR` - Request validation failed
- `NOT_FOUND` - Resource not found
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error
- `AI_UNAVAILABLE` - AI service temporarily unavailable

## Architecture

The application follows a layered architecture:

1. **API Layer**: FastAPI endpoints with request/response handling
2. **Service Layer**: Business logic and AI integration
3. **Repository Layer**: Database operations
4. **Domain Layer**: Entities and value objects

## MCP Integration

The MCP server exposes these tools:
- `create_todo` - Create a new todo
- `list_todos` - List todos with filters
- `update_todo` - Update an existing todo
- `delete_todo` - Delete a todo

## Roadmap

- **Phase 2**: User authentication and multi-user support
- **Phase 3**: Frontend with Next.js
- **Phase 4**: Docker and Kubernetes deployment
- **Phase 5**: Kafka messaging and DRP

## Constitution Compliance

This project adheres to the PROJECT_CONSTITUTION.md:
- ✅ Spec-driven development
- ✅ No manual coding by humans
- ✅ No feature invention beyond specification
- ✅ Clean architecture principles
- ✅ Phase governance (no Phase 2+ features)
- ✅ Technology constraints enforced
- ✅ Quality principles maintained

## License

[Add your license here]

## Contributing

[Add contribution guidelines]
