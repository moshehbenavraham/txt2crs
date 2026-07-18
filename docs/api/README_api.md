# API Documentation

## Overview

python-react-boilerplate provides REST API endpoints for authentication, user management, and item CRUD operations.

All endpoints except login require JWT authentication via Bearer token.

## OpenAPI Specification

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8012/docs
- **ReDoc**: http://localhost:8012/redoc
- **OpenAPI JSON**: http://localhost:8012/api/v1/openapi.json

## Authentication

All protected endpoints require a valid JWT token in the Authorization header:

```
Authorization: Bearer <token>
```

Obtain a token via POST `/api/v1/login/access-token`.

## Endpoints

### Login

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/login/access-token` | POST | Get JWT access token |
| `/api/v1/login/test-token` | POST | Test token validity |
| `/api/v1/password-recovery/{email}` | POST | Request password reset |
| `/api/v1/reset-password/` | POST | Reset password with token |

### Users

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/users/` | GET | List users (admin only) |
| `/api/v1/users/` | POST | Create user (admin only) |
| `/api/v1/users/me` | GET | Get current user |
| `/api/v1/users/me` | PATCH | Update current user |
| `/api/v1/users/me` | DELETE | Delete current user |
| `/api/v1/users/signup` | POST | Register new user |
| `/api/v1/users/{user_id}` | GET | Get user by ID |
| `/api/v1/users/{user_id}` | PATCH | Update user (admin only) |
| `/api/v1/users/{user_id}` | DELETE | Delete user (admin only) |

### Items

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/items/` | GET | List current user's items |
| `/api/v1/items/` | POST | Create item |
| `/api/v1/items/{id}` | GET | Get item by ID |
| `/api/v1/items/{id}` | PUT | Update item |
| `/api/v1/items/{id}` | DELETE | Delete item |

### Utils

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/utils/health-check/` | GET | Health check endpoint |
| `/api/v1/utils/test-email/` | POST | Test email sending (dev) |

## Error Responses

All API errors follow the standard FastAPI structure:

```json
{
  "detail": "Error message"
}
```

### HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Server Error |

## Client Generation

Frontend TypeScript client is auto-generated from OpenAPI spec:

```bash
# From project root
./scripts/generate-client.sh

# Or manually
cd frontend && npm run generate-client
```

Generated files:
- `frontend/src/client/sdk.gen.ts` - Service methods
- `frontend/src/client/types.gen.ts` - TypeScript types
