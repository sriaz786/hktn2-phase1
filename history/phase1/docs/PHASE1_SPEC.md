# Evolution of Todo - Phase 1 Specification

**Phase:** 1
**Status:** DRAFT
**Version:** 1.0
**Date:** 2025-01-06

---

## Constitution Compliance

This specification complies with **PROJECT_CONSTITUTION.md** v1.0:
- ✅ Spec-driven development workflow
- ✅ Agent behavior rules defined
- ✅ Phase governance and boundaries
- ✅ Technology constraints adhered to
- ✅ Quality principles applied

---

## 1. Phase Purpose

Establish a foundational todo management system with core CRUD operations, AI-powered task assistance, and MCP integration for extensibility. Phase 1 is backend-only, with no frontend component.

---

## 2. Phase Scope

### 2.1 In Scope
- Todo item management (Create, Read, Update, Delete)
- Task priority and status management
- Basic task metadata (title, description, due date, tags)
- AI-powered task assistance (task suggestions, prioritization help)
- MCP server integration for external tool connectivity
- RESTful API design
- Database schema with SQLModel
- Unit and integration tests
- API documentation (FastAPI auto-docs)

### 2.2 Out of Scope
- ❌ User authentication and authorization
- ❌ Multi-user support
- ❌ Frontend/UI (any kind)
- ❌ Real-time updates
- ❌ Advanced collaboration features
- ❌ Notifications
- ❌ Webhooks
- ❌ File attachments
- ❌ Complex workflows
- ❌ Dockerization
- ❌ Kubernetes deployment
- ❌ Message queuing
- ❌ Caching layer
- ❌ Monitoring/observability
- ❌ API versioning beyond v1

---

## 3. Functional Requirements

### 3.1 Todo Management

#### FR1: Create Todo
- System shall accept a POST request to create a new todo item
- Required fields: title
- Optional fields: description, due_date, priority, tags
- System shall generate a unique ID for each todo
- System shall set default priority to "medium"
- System shall set default status to "pending"
- System shall return the created todo with all fields

#### FR2: Read Todos
- System shall accept GET requests to retrieve todos
- System shall support retrieving a single todo by ID
- System shall support retrieving all todos
- System shall support filtering by: status, priority, tags
- System shall support sorting by: due_date, priority, created_at
- System shall return 404 for non-existent todo ID

#### FR3: Update Todo
- System shall accept PATCH requests to update existing todos
- System shall accept partial updates (only provided fields)
- System shall reject updates to immutable fields (id, created_at)
- System shall update modified_at timestamp on update
- System shall return 404 for non-existent todo ID
- System shall validate all updated fields

#### FR4: Delete Todo
- System shall accept DELETE requests to remove todos
- System shall return 204 No Content on successful deletion
- System shall return 404 for non-existent todo ID
- System shall perform soft delete (mark as deleted, don't remove from database)

#### FR5: Todo Status Management
- System shall support status values: pending, in_progress, completed, cancelled
- System shall allow status updates via PATCH
- System shall validate status transitions (optional: may allow any status for Phase 1)

#### FR6: Todo Priority Management
- System shall support priority values: low, medium, high, urgent
- System shall allow priority updates via PATCH
- System shall default to "medium" if not specified

### 3.2 AI-Powered Task Assistance

#### FR7: Task Suggestions
- System shall provide AI-powered suggestions for creating todos
- System shall accept a natural language description and generate structured todo suggestions
- System shall use OpenAI API for suggestion generation
- System shall return suggested title, description, and priority

#### FR8: Task Prioritization Help
- System shall provide AI recommendations for prioritizing existing todos
- System shall analyze todos based on due dates, priority, and content
- System shall return ranked list of todos with priority adjustment suggestions

#### FR9: Task Breakdown
- System shall accept a complex task and break it down into subtasks
- System shall use AI to decompose complex descriptions into manageable subtasks
- System shall suggest subtask dependencies where appropriate

### 3.3 MCP Integration

#### FR10: MCP Server
- System shall implement an MCP server
- System shall expose MCP tools for todo operations
- MCP tools shall include: create_todo, list_todos, update_todo, delete_todo

#### FR11: MCP Protocol Compliance
- System shall comply with MCP specification for tool definitions
- System shall provide JSON Schema for all MCP tool inputs/outputs
- System shall handle MCP protocol handshake and initialization

#### FR12: MCP External Tool Access
- System shall allow registration of external MCP clients
- System shall route MCP tool calls to appropriate handlers
- System shall return properly formatted MCP responses

### 3.4 API Design

#### FR13: RESTful Endpoints
- `POST /api/v1/todos` - Create todo
- `GET /api/v1/todos` - List todos (with query parameters for filter/sort)
- `GET /api/v1/todos/{id}` - Get specific todo
- `PATCH /api/v1/todos/{id}` - Update todo
- `DELETE /api/v1/todos/{id}` - Delete todo
- `POST /api/v1/ai/suggest` - Generate AI suggestions
- `POST /api/v1/ai/prioritize` - Get prioritization recommendations
- `POST /api/v1/ai/breakdown` - Break down task into subtasks

#### FR14: Request/Response Format
- All API requests and responses shall use JSON
- System shall use HTTP status codes appropriately
- Error responses shall include: error_code, message, details (optional)
- Success responses shall include data payload

#### FR15: Validation
- System shall validate all request inputs
- System shall return 400 Bad Request for validation errors
- System shall validate data types, required fields, and value ranges

---

## 4. Non-Functional Requirements

### 4.1 Performance
- API response time < 200ms for CRUD operations (p99)
- API response time < 1s for AI-powered operations (p99)
- Support up to 100 concurrent API requests
- Database query optimization for list operations

### 4.2 Reliability
- 99.5% uptime for API availability
- Automatic retry for transient database errors
- Graceful degradation if OpenAI API is unavailable
- Proper error handling and logging

### 4.3 Maintainability
- Code must follow clean architecture principles
- Clear separation of concerns (domain, API, infrastructure)
- Comprehensive docstrings for all public APIs
- Type hints for all Python code
- Unit test coverage > 80%
- Integration test coverage > 60%

### 4.4 Security
- Input validation for all endpoints
- Sanitization of user-provided data
- No SQL injection vulnerabilities (SQLModel parameter binding)
- Rate limiting on API endpoints (100 req/min per IP)
- API key management (configuration, not hardcoded)

### 4.5 Scalability
- Stateless API design
- Database connection pooling
- Efficient database queries (no N+1 queries)
- Prepared for future horizontal scaling

---

## 5. Data Model

### 5.1 Todo Entity

```python
class Todo(SQLModel, table=True):
    """Todo item entity"""

    id: int = Field(primary_key=True)
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[datetime] = None
    priority: Priority = Field(default=Priority.MEDIUM)
    status: Status = Field(default=Status.PENDING)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    modified_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = Field(default=False)

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Status(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

### 5.2 Database Schema
- Table: todos
- Indexes: id (primary), status, priority, due_date, is_deleted
- Foreign keys: None (Phase 1)

---

## 6. Architecture

### 6.1 Layered Architecture

```
┌─────────────────────────────────────┐
│      API Layer (FastAPI)           │
│  - Request/Response models          │
│  - Route handlers                  │
│  - Validation                       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Application Service Layer         │
│  - TodoService                      │
│  - AIService                        │
│  - MCPService                       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│   Domain Layer                     │
│  - Entities (Todo)                  │
│  - Value Objects (Priority, Status) │
│  - Domain logic                     │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Infrastructure Layer               │
│  - Database (SQLModel + Neon DB)    │
│  - OpenAI API integration           │
│  - MCP protocol implementation      │
└─────────────────────────────────────┘
```

### 6.2 Directory Structure

```
todo_project/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app initialization
│   ├── config.py                    # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── todos.py            # Todo endpoints
│   │   │   └── ai.py               # AI endpoints
│   ├── models/
│   │   ├── __init__.py
│   │   ├── todo.py                 # SQLModel entities
│   │   └── schemas.py              # Pydantic schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── todo_service.py         # Business logic for todos
│   │   ├── ai_service.py           # OpenAI integration
│   │   └── mcp_service.py          # MCP server
│   ├── repository/
│   │   ├── __init__.py
│   │   └── todo_repository.py      # Database operations
│   └── mcp/
│       ├── __init__.py
│       └── tools.py                # MCP tool definitions
├── tests/
│   ├── __init__.py
│   ├── test_todos.py
│   ├── test_ai_service.py
│   ├── test_mcp_service.py
│   └── test_integration/
│       └── test_api.py
├── requirements.txt
├── .env.example
├── pyproject.toml
└── README.md
```

---

## 7. Technology Stack

### 7.1 Backend
- **Language:** Python 3.11+
- **Web Framework:** FastAPI 0.109+
- **Database ORM:** SQLModel 0.0.14+
- **Database:** Neon DB (PostgreSQL 15+)
- **AI SDK:** OpenAI Agents SDK
- **MCP Protocol:** MCP Python SDK

### 7.2 Dependencies
```
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
sqlmodel>=0.0.14
psycopg2-binary>=2.9.9
openai>=1.6.0
anthropic>=0.18.0  # For Claude integration
mcp>=1.0.0  # MCP SDK
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0
pytest>=7.4.0
pytest-asyncio>=0.23.0
httpx>=0.26.0
```

### 7.3 Development Tools
- **Testing:** pytest, pytest-asyncio
- **Code Quality:** black, ruff, mypy
- **API Testing:** httpx (test client)

---

## 8. API Specification

### 8.1 Create Todo

**POST** `/api/v1/todos`

**Request Body:**
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive docs for Phase 1",
  "due_date": "2025-01-10T00:00:00Z",
  "priority": "high",
  "tags": ["documentation", "phase1"]
}
```

**Response (201 Created):**
```json
{
  "data": {
    "id": 1,
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for Phase 1",
    "due_date": "2025-01-10T00:00:00Z",
    "priority": "high",
    "status": "pending",
    "tags": ["documentation", "phase1"],
    "created_at": "2025-01-06T12:00:00Z",
    "modified_at": "2025-01-06T12:00:00Z"
  }
}
```

### 8.2 List Todos

**GET** `/api/v1/todos?status=pending&priority=high&sort_by=due_date`

**Response (200 OK):**
```json
{
  "data": [
    {
      "id": 1,
      "title": "Complete project documentation",
      "description": "Write comprehensive docs for Phase 1",
      "due_date": "2025-01-10T00:00:00Z",
      "priority": "high",
      "status": "pending",
      "tags": ["documentation", "phase1"],
      "created_at": "2025-01-06T12:00:00Z",
      "modified_at": "2025-01-06T12:00:00Z"
    }
  ],
  "metadata": {
    "total": 1,
    "page": 1,
    "page_size": 50
  }
}
```

### 8.3 Get Todo

**GET** `/api/v1/todos/{id}`

**Response (200 OK):**
```json
{
  "data": {
    "id": 1,
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for Phase 1",
    "due_date": "2025-01-10T00:00:00Z",
    "priority": "high",
    "status": "pending",
    "tags": ["documentation", "phase1"],
    "created_at": "2025-01-06T12:00:00Z",
    "modified_at": "2025-01-06T12:00:00Z"
  }
}
```

### 8.4 Update Todo

**PATCH** `/api/v1/todos/{id}`

**Request Body:**
```json
{
  "status": "in_progress",
  "priority": "urgent"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "id": 1,
    "title": "Complete project documentation",
    "description": "Write comprehensive docs for Phase 1",
    "due_date": "2025-01-10T00:00:00Z",
    "priority": "urgent",
    "status": "in_progress",
    "tags": ["documentation", "phase1"],
    "created_at": "2025-01-06T12:00:00Z",
    "modified_at": "2025-01-06T13:00:00Z"
  }
}
```

### 8.5 Delete Todo

**DELETE** `/api/v1/todos/{id}`

**Response (204 No Content)**

### 8.6 AI Suggestions

**POST** `/api/v1/ai/suggest`

**Request Body:**
```json
{
  "description": "I need to organize my project files and create documentation"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "suggestions": [
      {
        "title": "Organize project directory structure",
        "description": "Create logical folders for src, tests, docs, and assets",
        "priority": "high"
      },
      {
        "title": "Create project README",
        "description": "Write comprehensive README with setup instructions",
        "priority": "medium"
      }
    ]
  }
}
```

### 8.7 AI Prioritization

**POST** `/api/v1/ai/prioritize`

**Request Body:**
```json
{
  "todos": [
    {
      "id": 1,
      "title": "Complete documentation",
      "due_date": "2025-01-10T00:00:00Z",
      "priority": "medium"
    },
    {
      "id": 2,
      "title": "Fix critical bug",
      "due_date": "2025-01-07T00:00:00Z",
      "priority": "high"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "data": {
    "ranked_todos": [
      {
        "todo_id": 2,
        "title": "Fix critical bug",
        "recommended_priority": "urgent",
        "reasoning": "Critical issue with imminent due date"
      },
      {
        "todo_id": 1,
        "title": "Complete documentation",
        "recommended_priority": "high",
        "reasoning": "Important but has more time"
      }
    ]
  }
}
```

### 8.8 AI Task Breakdown

**POST** `/api/v1/ai/breakdown`

**Request Body:**
```json
{
  "task": "Build a complete REST API with authentication, database, and testing"
}
```

**Response (200 OK):**
```json
{
  "data": {
    "subtasks": [
      {
        "title": "Design API endpoints and data models",
        "estimated_order": 1,
        "dependencies": []
      },
      {
        "title": "Implement database schema and migrations",
        "estimated_order": 2,
        "dependencies": [1]
      },
      {
        "title": "Create API route handlers",
        "estimated_order": 3,
        "dependencies": [2]
      },
      {
        "title": "Write unit tests",
        "estimated_order": 4,
        "dependencies": [3]
      }
    ]
  }
}
```

### 8.9 Error Responses

**400 Bad Request (Validation Error):**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request data",
    "details": {
      "title": ["This field is required"]
    }
  }
}
```

**404 Not Found:**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Todo with id 999 not found"
  }
}
```

**429 Too Many Requests:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 60 seconds."
  }
}
```

**500 Internal Server Error:**
```json
{
  "error": {
    "code": "INTERNAL_ERROR",
    "message": "An unexpected error occurred"
  }
}
```

---

## 9. AI Integration Details

### 9.1 OpenAI Configuration
- Model: GPT-4 or GPT-3.5-turbo (configurable)
- Temperature: 0.3 (for consistent outputs)
- Max tokens: 500
- Retry logic: 3 retries with exponential backoff

### 9.2 Prompt Templates

#### Task Suggestion Prompt
```
Given the following task description, suggest 3-5 structured todo items.

Description: {description}

For each suggestion, provide:
- title (concise, action-oriented)
- description (brief explanation)
- priority (low/medium/high/urgent)

Respond in JSON format:
{
  "suggestions": [
    {"title": "...", "description": "...", "priority": "..."}
  ]
}
```

#### Prioritization Prompt
```
Analyze and prioritize these todo items based on due dates, current priorities, and content importance.

Todos: {todos_json}

Provide:
- Ranked list of todos
- Recommended priority adjustment if needed
- Brief reasoning for ranking

Respond in JSON format:
{
  "ranked_todos": [
    {"todo_id": 1, "recommended_priority": "...", "reasoning": "..."}
  ]
}
```

#### Task Breakdown Prompt
```
Break down the following complex task into manageable subtasks with dependencies.

Task: {task}

Provide:
- Subtasks in logical order
- Dependencies between subtasks
- Estimated execution order

Respond in JSON format:
{
  "subtasks": [
    {"title": "...", "estimated_order": 1, "dependencies": [0]}
  ]
}
```

### 9.3 Fallback Behavior
- If OpenAI API is unavailable, return predefined suggestions
- Log all API failures for monitoring
- Cache common AI responses to reduce API calls

---

## 10. MCP Integration Details

### 10.1 MCP Tool Definitions

#### create_todo
```json
{
  "name": "create_todo",
  "description": "Create a new todo item",
  "inputSchema": {
    "type": "object",
    "properties": {
      "title": {"type": "string"},
      "description": {"type": "string"},
      "due_date": {"type": "string", "format": "date-time"},
      "priority": {"enum": ["low", "medium", "high", "urgent"]}
    },
    "required": ["title"]
  }
}
```

#### list_todos
```json
{
  "name": "list_todos",
  "description": "List all todo items with optional filters",
  "inputSchema": {
    "type": "object",
    "properties": {
      "status": {"enum": ["pending", "in_progress", "completed", "cancelled"]},
      "priority": {"enum": ["low", "medium", "high", "urgent"]}
    }
  }
}
```

#### update_todo
```json
{
  "name": "update_todo",
  "description": "Update an existing todo item",
  "inputSchema": {
    "type": "object",
    "properties": {
      "id": {"type": "integer"},
      "title": {"type": "string"},
      "description": {"type": "string"},
      "status": {"enum": ["pending", "in_progress", "completed", "cancelled"]},
      "priority": {"enum": ["low", "medium", "high", "urgent"]}
    },
    "required": ["id"]
  }
}
```

#### delete_todo
```json
{
  "name": "delete_todo",
  "description": "Delete a todo item",
  "inputSchema": {
    "type": "object",
    "properties": {
      "id": {"type": "integer"}
    },
    "required": ["id"]
  }
}
```

### 10.2 MCP Server Configuration
- Transport: WebSocket (or HTTP)
- Server name: "todo-server"
- Version: 1.0.0
- Capabilities: tools

### 10.3 MCP Protocol Flow
1. Client connects and initializes
2. Server advertises available tools
3. Client requests tool list
4. Client calls tool with parameters
5. Server executes and returns result
6. Error handling with proper error codes

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Test repository layer (CRUD operations)
- Test service layer (business logic)
- Test validation logic
- Test AI service with mocked OpenAI responses
- Test MCP tool handlers

### 11.2 Integration Tests
- Test API endpoints with test database
- Test end-to-end todo workflows
- Test AI endpoints with mocked AI
- Test MCP tool execution
- Test error scenarios

### 11.3 Test Coverage Goals
- Overall coverage: > 80%
- Service layer: > 90%
- Repository layer: > 85%
- API layer: > 75%

### 11.4 Test Data
- Use factory fixtures for test data
- Seed test database with consistent data
- Clean up between tests

---

## 12. Configuration

### 12.1 Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:password@neon-host/dbname

# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4

# API
API_HOST=0.0.0.0
API_PORT=8000
API_RATE_LIMIT=100

# MCP
MCP_ENABLED=true
MCP_PORT=3000

# Logging
LOG_LEVEL=INFO
```

### 12.2 Configuration Management
- Use Pydantic Settings for configuration
- Load from environment variables
- Support .env files for development
- Validate all configuration on startup

---

## 13. Logging and Monitoring

### 13.1 Logging
- Use Python logging module
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Structured logging with JSON format
- Log: API requests, errors, AI calls, MCP operations

### 13.2 Log Format
```json
{
  "timestamp": "2025-01-06T12:00:00Z",
  "level": "INFO",
  "message": "Todo created",
  "context": {
    "todo_id": 1,
    "request_id": "abc123"
  }
}
```

### 13.3 Health Check
- Endpoint: `GET /health`
- Response: `{"status": "healthy"}`
- Check: Database connection, OpenAI API availability

---

## 14. Deliverables

### 14.1 Code
- Complete Python FastAPI application
- All API endpoints implemented
- Database models and migrations
- AI integration service
- MCP server implementation
- Configuration management
- Logging setup

### 14.2 Tests
- Unit tests (80%+ coverage)
- Integration tests
- Test fixtures and utilities

### 14.3 Documentation
- API documentation (auto-generated by FastAPI)
- README with setup instructions
- Configuration guide
- MCP integration guide

### 14.4 Configuration Files
- requirements.txt
- .env.example
- pyproject.toml
- .gitignore

---

## 15. Success Criteria

Phase 1 is considered complete when:

- ✅ All API endpoints (FR1-FR15) are implemented and tested
- ✅ AI-powered features (FR7-FR9) are working
- ✅ MCP integration (FR10-FR12) is functional
- ✅ Database schema is implemented in Neon DB
- ✅ Unit test coverage exceeds 80%
- ✅ Integration tests pass
- ✅ API documentation is available at /docs
- ✅ Health check endpoint returns healthy
- ✅ All code follows quality principles (clean architecture, type hints, docstrings)
- ✅ No manual coding by humans (per Constitution)
- ✅ All code traces back to approved specification (per Constitution)
- ✅ No Phase 2+ features leaked into Phase 1 (per Constitution)

---

## 16. Assumptions and Dependencies

### 16.1 Assumptions
- Neon DB account is available
- OpenAI API access with sufficient quota
- Python 3.11+ environment
- No authentication required for Phase 1

### 16.2 Dependencies
- External: OpenAI API, Neon DB
- Internal: PROJECT_CONSTITUTION.md
- Future: Phase 2 specification (for next phase planning)

---

## 17. Risks and Mitigations

### 17.1 Risks
- **OpenAI API downtime**: Mitigation: Fallback to predefined responses
- **Neon DB connection issues**: Mitigation: Connection pooling, retry logic
- **MCP protocol changes**: Mitigation: Version pinning, upgrade plan
- **AI cost overruns**: Mitigation: Response caching, limit usage

### 17.2 Mitigation Actions
- Monitor API usage and costs
- Implement circuit breakers for external services
- Log all failures for investigation
- Have rollback plan for deployments

---

## 18. Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0 | 2025-01-06 | Initial specification | AI Agent |

---

**END OF PHASE 1 SPECIFICATION**
