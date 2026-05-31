# Task Management System

A FastAPI-based task management application with role-based access control, JWT authentication, and a layered architecture following Domain-Driven Design principles.

---

## Table of Contents
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [API Usage Guide](#api-usage-guide)
- [Architecture Explanation](#architecture-explanation)
- [Assumptions and Limitations](#assumptions-and-limitations)

---

## Setup Instructions

### Prerequisites
- Docker and Docker Compose installed
- Git

### 1. Clone the repository
```bash
git clone <repository-url>
cd task_management_system
```

### 2. Create environment files inside root directory
```bash
touch .env .env.db
```
- Copy variables from `.env.example` to `.env`
- Copy variables from `.env.db.example` to `.env.db`

### 3. Make entrypoint script executable
```bash
chmod +x entrypoint.sh
```

### 4. Create Docker volume and network
Remove existing volume or network if they already exist.
```bash
docker volume create postgres_data
docker volume create redis_data
docker network create task_management_system_network
```

### 5. Build and start containers
```bash
docker compose up -d --build
```

Verify containers are running:
```bash
docker container ls
```

View logs of a specific container:
```bash
docker logs -f <container_name>
```

### 6. Seed the database
**Important: Do not skip this step.** This command creates admin user, dummy users, roles, and permissions.
```bash
docker exec -it task_management_app python3 seed.py
```

---

## Environment Variables

### `.env`
| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | JWT signing secret key | `your-secret-key` |
| `JWT_ALGORITHM` | JWT hashing algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiry duration in minutes | `60` |
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://user:pass@db:5432/dbname` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |

### `.env.db`
| Variable | Description | Example |
|---|---|---|
| `POSTGRES_USER` | PostgreSQL username | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `postgres` |
| `POSTGRES_DB` | PostgreSQL database name | `task_management` |

---

## API Usage Guide

### Authentication

#### Login
```
POST /api/v1/auth/login
```
Request body:
```json
{
    "email": "admin@example.com",
    "password": "password"
}
```
Response:
```json
{
    "access_token": "<jwt_token>",
    "token_type": "Bearer"
}
```

All subsequent requests must include the token in the `Authorization` header:
```
Authorization: Bearer <jwt_token>
```

---

### Tasks

#### List Tasks
```
GET /api/v1/tasks/
```
Query parameters:
| Parameter | Type | Description |
|---|---|---|
| `status_filter` | int | Filter by task status |
| `due_date_from` | str | Filter tasks from this date |
| `due_date_to` | str | Filter tasks up to this date |

#### Get Task
```
GET /api/v1/tasks/{task_id}
```
Response:
```json
{
    "id": 1,
    "title": "Fix login bug",
    "description": "Users are unable to login with correct credentials",
    "due_date": "2024-12-31",
    "status": 1,
    "assigned_to": {
        "id": 2,
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com"
    },
    "created_by": {
        "id": 1,
        "first_name": "Admin",
        "last_name": "User",
        "email": "admin@example.com"
    }
}
```

#### Create Task
```
POST /api/v1/tasks/
```
Request body:
```json
{
    "title": "Fix login bug",
    "description": "Users are unable to login with correct credentials",
    "due_date": "2024-12-31",
    "assigned_to_id": 2,
    "created_by_id": 1
}
```

#### Update Task
```
PUT /api/v1/tasks/{task_id}
```
Request body: same as create task.

#### Update Task Status
```
PATCH /api/v1/tasks/{task_id}/status
```
Request body:
```json
{
    "status": 2
}
```

#### Delete Task
```
DELETE /api/v1/tasks/{task_id}
```
Response:
```json
{
    "detail": "Task deleted successfully."
}
```

---

### Users

#### List Users
```
GET /api/v1/users/
```
Query parameters:
| Parameter | Type | Description |
|---|---|---|
| `manager_id` | int | Filter users by their manager |

Response:
```json
[
    {
        "id": 1,
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "is_active": true,
        "role_id": 2,
        "role": "MANAGER",
        "manager_id": 1
    }
]
```

---

### Roles and Permissions

Roles and permissions are seeded automatically via `seed.py`. The default roles are:

| Role | Permissions |
|---|---|
| `ADMIN` | Full access to all tasks and users |
| `MANAGER` | Create, update, view tasks assigned to or created by them |
| `USER` | View and update status of tasks assigned to them |

---

## Architecture Explanation

The project follows a layered architecture based on Domain-Driven Design (DDD) principles.

```
task-management-system/
├── alembic/                         # Database migrations
│   ├── versions/
│   │   └── 65dbfb21edf2_initial.py
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   ├── common/                      # Shared utilities across all bounded contexts
│   │   ├── models.py                # Shared base Pydantic models
│   │   ├── constants.py             # Global permission name constants
│   │   ├── permissions.py           # PermissionChecker implementation
│   │   ├── permission_decorator.py  # require_permission decorator
│   │   └── unit_of_work.py          # UnitOfWork pattern
│   │
│   ├── task/                        # Task bounded context
│   │   ├── adapters/
│   │   │   ├── orm.py               # SQLAlchemy ORM models
│   │   │   └── repositories.py      # Repository implementation
│   │   ├── domain/
│   │   │   ├── models.py            # Pydantic domain models
│   │   │   ├── commands.py          # Command objects
│   │   │   └── enumns.py            # TaskStatus enum
│   │   ├── service_layer/
│   │   │   ├── services.py          # Business logic
│   │   │   └── exceptions.py        # Domain exceptions
│   │   ├── common/
│   │   │   ├── constants.py         # Task-specific constants
│   │   │   └── dependencies.py      # FastAPI service dependencies
│   │   └── entrypoints/
│   │       └── routes.py            # API route handlers
│   │
│   ├── user/                        # User bounded context
│   │   ├── adapters/
│   │   │   ├── orm.py
│   │   │   └── repositories.py
│   │   ├── domain/
│   │   │   ├── models.py
│   │   │   ├── commands.py
│   │   │   └── exceptions.py
│   │   ├── service_layer/
│   │   │   ├── services.py
│   │   │   └── exceptions.py
│   │   ├── common/
│   │   │   ├── constants.py
│   │   │   └── dependencies.py
│   │   └── entrypoint/
│   │       └── routes.py
│   │
│   ├── role_permission/             # Role and permission bounded context
│   │   ├── adapters/
│   │   │   ├── orm.py
│   │   │   └── repositories.py
│   │   └── common/
│   │       └── constants.py
│   │
│   ├── middlewares/
│   │   └── auth_middleware.py       # JWT authentication middleware
│   │
│   ├── database.py                  # Database session and engine setup
│   ├── settings.py                  # Pydantic settings / environment config
│   ├── security.py                  # AuthHandler for JWT and password hashing
│   └── main.py                      # FastAPI app entrypoint
│
├── seed.py                          # Database seeding script
├── entrypoint.sh                    # Docker entrypoint script
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
└── README.md
```

### Key Patterns

**Repository Pattern** — Each bounded context has its own repository that abstracts all database queries. The service layer never interacts with SQLAlchemy directly.

**Unit of Work** — Wraps the SQLAlchemy async session and exposes repositories as properties. Commits on success and rolls back on any exception, ensuring transactional consistency per request.

**Service Layer** — Contains all business logic including permission checks, domain rule enforcement (e.g. a completed task cannot be updated), and orchestration of repository calls.

**Domain Models** — Pydantic models represent the domain entities and are kept completely separate from ORM models. Repositories map ORM objects to plain dictionaries via `_to_dict` before returning them to the service layer.

**Command Objects** — Incoming data is modelled as command objects (e.g. `CreateTaskCommand`, `UpdateTaskCommand`) that extend domain models, keeping the service layer interface explicit and type-safe.

**Permission Checker** — `PermissionChecker` is injected into the service layer and validates role-based permissions against the database before any operation is performed.

**JWT Middleware** — Validates the JWT token on every incoming request (except exempt paths like `/api/v1/auth/login`) and attaches `user_id`, `role_id`, and `email` to `request.state` for use throughout the request lifecycle.

---

## Assumptions and Limitations

### Assumptions
- A user has exactly one role assigned at registration time.
- Task status is represented as an integer internally and mapped to a string constant (e.g. `STR_COMPLETED`) for business rule checks.
- Only the task creator or a user with `DELETE_ANY_TASK` permission can delete a task.
- A completed task cannot be updated — any update attempt raises `TaskAlreadyCompletedError`.
- `ADMIN` users can view all tasks; `MANAGER` and `USER` roles are restricted to tasks they are directly involved in.
- The `manager_id` field on a user is self-referential — a manager is also a user in the system.
- Roles and permissions are static and managed via `seed.py` rather than through the API.

### Limitations
- No pagination is implemented on list endpoints — large datasets may cause slow responses.
- No soft delete — deleted tasks are permanently removed from the database.
- Token refresh is not implemented — once a token expires the user must log in again.
- No email notification system when a task is assigned or its status changes.
- Filters on the list tasks endpoint are limited to `status`, `due_date_from`, and `due_date_to` — no full-text search on title or description.
- Role and permission management (create/update/delete) is not exposed via API — changes must be made directly via `seed.py` or database migrations.
- No test suite is included — unit and integration tests are not yet implemented.
```
