# Code Examples for AI Agents

> Curated examples demonstrating patterns used in this codebase. Research shows 3-5 well-commented examples achieve 85%+ accuracy on domain-specific code generation.

## Usage

When implementing new features, reference these examples to follow established patterns:

```python
# Before implementing, check for relevant example
# e.g., "Create a new CRUD function" -> see examples/backend/crud/
```

## Directory Structure

```
examples/
├── backend/
│   ├── crud/                    # Database operations
│   │   ├── create_with_validation.py
│   │   ├── paginated_list.py
│   │   └── update_partial.py
│   ├── api/                     # API endpoint patterns
│   │   ├── authenticated_endpoint.py
│   │   └── error_handling.py
│   └── testing/                 # Test patterns
│       └── unit_test_crud.py
├── frontend/
│   ├── hooks/                   # Custom React hooks
│   │   ├── use_mutation_with_toast.ts
│   │   └── use_query_with_suspense.ts
│   └── components/              # React components
│       └── form_with_validation.tsx
└── README_examples.md
```

## Example Format

Each example includes:

1. **Header docstring** with:
   - `PATTERN`: Name of the pattern
   - `USE WHEN`: Scenarios where this pattern applies
   - `TAGS`: Searchable keywords

2. **Inline comments** explaining key decisions

3. **Usage example** at the bottom

## Tags Reference

| Tag | Meaning |
|-----|---------|
| `crud` | Database CRUD operations |
| `api` | API route handlers |
| `auth` | Authentication required |
| `validation` | Input validation |
| `pagination` | List endpoints with skip/limit |
| `mutation` | TanStack Query mutations |
| `form` | Form handling with validation |
| `toast` | User feedback notifications |
| `error-handling` | Error handling patterns |

## For AI Agents

When asked to implement a feature:

1. Search examples by pattern name or tags
2. Identify the most relevant example
3. Adapt the pattern to the specific use case
4. Maintain the same code style and conventions

**Important**: Examples use actual imports from this codebase. Replace placeholder values with real data.
