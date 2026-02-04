# Project Instructions for Claude Code

> This file is automatically loaded into context when Claude Code starts.

## Project Overview

This is a Python backend API built with FastAPI. It provides [BRIEF_DESCRIPTION] for [TARGET_USERS].

**Tech Stack:**
- Python 3.11+
- FastAPI for API framework
- SQLAlchemy 2.0 for ORM
- Alembic for migrations
- PostgreSQL for database
- Pydantic for validation
- pytest for testing

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     FastAPI App                          │
├─────────────────────────────────────────────────────────┤
│  Routers          │  Dependencies     │  Middleware      │
│  └── v1/          │  └── auth         │  └── cors        │
│      └── users    │  └── database     │  └── logging     │
├─────────────────────────────────────────────────────────┤
│  Services (Business Logic)                               │
├─────────────────────────────────────────────────────────┤
│  Repositories (Data Access)                              │
├─────────────────────────────────────────────────────────┤
│  SQLAlchemy Models          │  Pydantic Schemas          │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
├── src/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/       # Route handlers
│   │   │   └── router.py        # API router
│   │   └── dependencies.py      # Shared dependencies
│   ├── core/
│   │   ├── config.py            # Settings management
│   │   ├── security.py          # Auth utilities
│   │   └── exceptions.py        # Custom exceptions
│   ├── db/
│   │   ├── models/              # SQLAlchemy models
│   │   ├── repositories/        # Data access layer
│   │   └── session.py           # Database session
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   └── main.py                  # Application entry
├── alembic/                     # Database migrations
├── tests/                       # Test files
└── CLAUDE.md                   # This file
```

## Development Commands

### Setup & Run
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run development server
uvicorn src.main:app --reload --port 8000

# Run with specific host
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Database
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show migration history
alembic history
```

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_users.py

# Run tests matching pattern
pytest -k "test_create"

# Run with verbose output
pytest -v
```

### Linting & Formatting
```bash
# Format code
black src tests
isort src tests

# Lint
ruff check src tests

# Type checking
mypy src
```

## Code Style & Conventions

### Endpoint Structure
```python
# api/v1/endpoints/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db, get_current_user
from src.schemas.user import UserCreate, UserResponse
from src.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Create a new user."""
    service = UserService(db)
    return await service.create(user_in)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get user by ID."""
    service = UserService(db)
    user = await service.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### Service Layer
```python
# services/user_service.py
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.repositories.user_repository import UserRepository
from src.schemas.user import UserCreate, UserUpdate


class UserService:
    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create(self, user_in: UserCreate) -> User:
        # Business logic here
        return await self.repository.create(user_in)

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.repository.get(user_id)
```

### Pydantic Schemas
```python
# schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None


class UserResponse(UserBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
```

### SQLAlchemy Models
```python
# db/models/user.py
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
```

### Naming Conventions
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Variables**: `snake_case`
- **Constants**: `SCREAMING_SNAKE_CASE`
- **Private**: Prefix with `_`

## Testing Requirements

- All endpoints must have tests
- Aim for 85% coverage on new code
- Use fixtures for common setup

### Test Structure
```python
# tests/test_users.py
import pytest
from httpx import AsyncClient

from src.main import app


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(db_session):
    # Create test user
    ...


class TestCreateUser:
    async def test_create_user_success(self, client: AsyncClient):
        response = await client.post(
            "/api/v1/users/",
            json={"email": "test@example.com", "name": "Test", "password": "secret"},
        )
        assert response.status_code == 201
        assert response.json()["email"] == "test@example.com"

    async def test_create_user_duplicate_email(self, client: AsyncClient, test_user):
        response = await client.post(
            "/api/v1/users/",
            json={"email": test_user.email, "name": "Test", "password": "secret"},
        )
        assert response.status_code == 400
```

## Git Workflow

### Commit Messages
```
feat(users): add password reset endpoint
fix(auth): handle expired refresh tokens
refactor(db): migrate to async SQLAlchemy
```

### Branch Naming
- `feature/user-registration`
- `fix/token-expiration`
- `refactor/async-db`

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `SECRET_KEY` | JWT signing key | Yes |
| `ENVIRONMENT` | dev/staging/prod | Yes |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | No |
| `SENTRY_DSN` | Sentry error tracking | No |

## Known Issues & Gotchas

- **Async SQLAlchemy**: Use `AsyncSession`, not `Session`
- **Alembic autogenerate**: Review generated migrations before applying
- **Pydantic v2**: Use `model_config` instead of `class Config`
- **Type hints**: SQLAlchemy 2.0 requires `Mapped[]` annotations

## Rules for Claude

1. **Think first, code second**: Understand the domain before writing
2. **Follow the layer pattern**: Router → Service → Repository
3. **Validate at boundaries**: Use Pydantic for all external data
4. **Async everywhere**: Use async/await consistently
5. **Type everything**: Full type hints, no `Any` without justification
6. **Test behavior**: Test endpoints and services, not implementation
