# File Organization Guide

> Directory structure and naming conventions for the Python React Boilerplate

## Project Root Structure

```
python-react-boilerplate/
├── backend/                    # Python FastAPI backend
├── frontend/                   # React TypeScript frontend
├── docs/                       # Project documentation
├── scripts/                    # Utility scripts
├── .github/                    # GitHub Actions workflows
├── docker-compose.yml          # Local development orchestration
├── docker-compose.override.yml # Local overrides (gitignored)
├── .env.example                # Environment template
├── .env                        # Local environment (gitignored)
├── .pre-commit-config.yaml     # Pre-commit hooks
├── AGENTS.md                   # AI agent instructions
├── CLAUDE.md                   # Symlink to AGENTS.md
├── llms.txt                    # LLM discovery file
└── README.md                   # Project overview
```

## Backend Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── models.py               # SQLModel database models + Pydantic schemas
│   ├── crud.py                 # Database operations (Create, Read, Update, Delete)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py             # API router aggregation
│   │   ├── deps.py             # Dependency injection (auth, db session)
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── login.py        # Authentication endpoints
│   │       ├── users.py        # User management endpoints
│   │       ├── items.py        # Item CRUD endpoints
│   │       └── utils.py        # Health check, etc.
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Settings and configuration
│   │   ├── constants.py        # Application constants and enums
│   │   ├── db.py               # Database session management
│   │   ├── security.py         # JWT, password hashing
│   │   ├── exceptions.py       # Custom exception classes
│   │   ├── rate_limit.py       # Rate limiting configuration
│   │   └── http_utils.py       # HTTP utilities
│   ├── email-templates/        # Jinja2 email templates
│   │   ├── src/
│   │   │   └── *.mjml          # MJML source files
│   │   └── build/
│   │       └── *.html          # Compiled HTML (auto-generated)
│   └── tests/                  # Backend tests (alternative location)
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   └── env.py                  # Alembic configuration
├── scripts/
│   └── test.sh                 # Test runner script
├── tests/                      # Primary test location
│   ├── conftest.py             # Pytest fixtures
│   ├── test_*.py               # Test modules
│   └── api/
│       └── routes/
│           └── test_*.py       # Route-specific tests
├── pyproject.toml              # Python project configuration
├── Dockerfile                  # Backend Docker image
├── AGENTS.md                   # Backend-specific AI instructions
└── DEPENDENCIES.md             # Dependency documentation
```

## Frontend Structure

```
frontend/
├── src/
│   ├── main.tsx                # Application entry point
│   ├── routeTree.gen.ts        # Auto-generated route tree (DO NOT EDIT)
│   ├── routes/
│   │   ├── __root.tsx          # Root layout
│   │   ├── _layout.tsx         # Authenticated layout wrapper
│   │   ├── _layout/
│   │   │   ├── index.tsx       # Dashboard (/)
│   │   │   ├── items.tsx       # Items page
│   │   │   ├── settings.tsx    # User settings
│   │   │   └── admin.tsx       # Admin panel
│   │   ├── login.tsx           # Login page
│   │   ├── signup.tsx          # Registration page
│   │   └── reset-password.tsx  # Password reset
│   ├── components/
│   │   ├── ui/                 # shadcn/ui components (DO NOT EDIT directly)
│   │   ├── Common/             # Shared components
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── ActionsMenu.tsx
│   │   ├── Items/              # Feature-specific components
│   │   │   ├── AddItem.tsx
│   │   │   └── EditItem.tsx
│   │   └── UserSettings/
│   │       ├── Appearance.tsx
│   │       └── ChangePassword.tsx
│   ├── hooks/
│   │   ├── useAuth.ts          # Authentication hook
│   │   └── useCustomToast.ts   # Toast notifications
│   ├── client/                 # Auto-generated API client (DO NOT EDIT)
│   │   ├── index.ts
│   │   ├── core/
│   │   ├── models/
│   │   └── services/
│   ├── lib/
│   │   └── utils.ts            # Utility functions
│   └── theme.tsx               # Theme configuration
├── public/                     # Static assets
├── tests/
│   └── *.spec.ts               # Playwright E2E tests
├── package.json                # NPM dependencies
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
├── tailwind.config.ts          # Tailwind CSS configuration
├── biome.json                  # Biome linter configuration
├── playwright.config.ts        # Playwright test configuration
├── Dockerfile                  # Frontend Docker image
└── AGENTS.md                   # Frontend-specific AI instructions
```

## Documentation Structure

```
docs/
├── adr/                        # Architecture Decision Records
│   ├── README.md               # ADR index
│   ├── _template.md            # ADR template
│   └── 0001-*.md               # Individual ADRs
├── database/
│   └── SCHEMA.md               # Database schema documentation
├── ongoing-roadmap/              # Roadmap and planning docs
├── CONFIGURATION.md            # Environment variables
├── ENVIRONMENTS.md             # Environment-specific behavior
├── FILE_ORGANIZATION.md        # This file
├── ANTI_PATTERNS.md            # What not to do
├── DATABASE_MIGRATIONS.md      # Migration workflow
├── FRONTEND_ERROR_HANDLING.md  # Frontend error strategy
└── SECURITY.md                 # Security policy
```

## Naming Conventions

### Files

| Type | Convention | Example |
|------|------------|---------|
| Python modules | snake_case | `user_service.py` |
| Python test files | `test_*.py` | `test_users.py` |
| TypeScript/React | PascalCase | `UserSettings.tsx` |
| TypeScript hooks | camelCase with `use` prefix | `useAuth.ts` |
| TypeScript tests | `*.spec.ts` or `*.test.ts` | `login.spec.ts` |
| Documentation | UPPER_CASE or Title-Case | `README.md`, `SECURITY.md` |
| Configuration | dot prefix or lowercase | `.env`, `docker-compose.yml` |

### Directories

| Type | Convention | Example |
|------|------------|---------|
| Python packages | snake_case | `api/routes/` |
| React components | PascalCase | `UserSettings/` |
| Feature modules | PascalCase | `Items/`, `Common/` |
| Config/tooling | lowercase | `scripts/`, `docs/` |

### Code Elements

| Element | Convention | Example |
|---------|------------|---------|
| Python classes | PascalCase | `UserCreate` |
| Python functions | snake_case | `get_user_by_email` |
| Python constants | UPPER_SNAKE_CASE | `MAX_ITEMS_PER_PAGE` |
| TypeScript interfaces | PascalCase | `UserPublic` |
| TypeScript functions | camelCase | `handleSubmit` |
| React components | PascalCase | `AddItemModal` |
| CSS classes | kebab-case (via Tailwind) | `text-gray-500` |

## Auto-Generated Files

**DO NOT EDIT** these files manually:

| File/Directory | Generator | Command |
|----------------|-----------|---------|
| `frontend/src/client/` | OpenAPI Generator | `npm run generate-client` |
| `frontend/src/routeTree.gen.ts` | TanStack Router | Auto on file changes |
| `backend/alembic/versions/*.py` | Alembic | `alembic revision --autogenerate` |
| `backend/app/email-templates/build/` | MJML | `npm run build-emails` |

## Test File Location

Tests can be organized in two ways:

### Option 1: Dedicated Test Directory (Current)
```
backend/
├── app/
│   └── api/routes/users.py
└── tests/
    └── api/routes/test_users.py
```

### Option 2: Co-located Tests
```
backend/app/
├── api/routes/
│   ├── users.py
│   └── __tests__/
│       └── test_users.py
```

Currently, this project uses Option 1. If changing, update `pytest.ini_options` in `pyproject.toml`.

## Adding New Features

### New Backend Endpoint

1. Create/update model in `backend/app/models.py`
2. Add CRUD functions in `backend/app/crud.py`
3. Create route in `backend/app/api/routes/`
4. Register router in `backend/app/api/main.py`
5. Add tests in `backend/tests/api/routes/`
6. Regenerate frontend client: `cd frontend && npm run generate-client`

### New Frontend Page

1. Create route file in `frontend/src/routes/`
2. TanStack Router auto-generates route tree
3. Add navigation link if needed
4. Add E2E tests in `frontend/tests/`

### New React Component

1. Create in `frontend/src/components/[Feature]/`
2. Use PascalCase naming
3. Export from component file
4. Group related components in feature directories

## Import Conventions

### Backend

```python
# Standard library
from typing import Annotated
from uuid import UUID

# Third-party
from fastapi import APIRouter, Depends
from sqlmodel import Session

# Local application
from app.core.config import settings
from app.core.constants import ErrorCode
from app.models import User, UserCreate
from app import crud
```

### Frontend

```typescript
// React and external libraries
import { useState } from "react"
import { useQuery } from "@tanstack/react-query"

// Internal aliases (@/)
import { UsersService } from "@/client"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"

// Relative imports (same feature)
import { UserCard } from "./UserCard"
```
