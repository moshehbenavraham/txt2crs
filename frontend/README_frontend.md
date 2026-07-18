# Python React Boilerplate - Frontend

The frontend is built with [Vite](https://vitejs.dev/), [React](https://reactjs.org/), [TypeScript](https://www.typescriptlang.org/), [TanStack Query](https://tanstack.com/query), [TanStack Router](https://tanstack.com/router), and [Tailwind CSS](https://tailwindcss.com/).

## Pages

| Route | File | Description |
|-------|------|-------------|
| `/` | `src/routes/_layout/index.tsx` | Dashboard |
| `/login` | `src/routes/login.tsx` | User login |
| `/signup` | `src/routes/signup.tsx` | User registration |
| `/items` | `src/routes/_layout/items.tsx` | Item management |
| `/settings` | `src/routes/_layout/settings.tsx` | User settings |
| `/admin` | `src/routes/_layout/admin.tsx` | Admin panel (superusers) |
| `/recover-password` | `src/routes/recover-password.tsx` | Password recovery |
| `/reset-password` | `src/routes/reset-password.tsx` | Password reset |

## Components

### Common (`src/components/Common/`)

Shared UI components used across the application.

### Items (`src/components/Items/`)

- **ItemsTable** - Paginated items list with filtering
- **AddItem** - Create new item modal
- **EditItem** - Edit item modal
- **DeleteItem** - Delete confirmation modal
- **ContentTypeBadge** - Item type badge display
- **ContentTypeFilter** - Filter items by type

### Admin (`src/components/Admin/`)

- **AddUser** - Create user form
- **EditUser** - Edit user form
- **DeleteUser** - Delete user confirmation

### Sidebar (`src/components/Sidebar/`)

- **AppSidebar** - Main navigation sidebar

## Hooks

| Hook | File | Purpose |
|------|------|---------|
| `useAuth` | `hooks/useAuth.ts` | Authentication state and actions |
| `useSaveToItems` | `hooks/useSaveToItems.ts` | Save content to Items |
| `useCustomToast` | `hooks/useCustomToast.ts` | Toast notification helpers |

## Frontend Development

Before you begin, ensure Node Version Manager (nvm) or Fast Node Manager (fnm) is installed.

### Setup

```bash
cd frontend

# Install Node.js version from .nvmrc
fnm install  # or: nvm install

# Switch to correct version
fnm use  # or: nvm use

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open http://localhost:5183 in your browser.

## Generate Client

The TypeScript client is auto-generated from the backend OpenAPI spec.

### Automatic

```bash
# From project root
./scripts/generate-client.sh
```

### Manual

1. Start Docker Compose stack
2. Download `http://localhost:8012/api/v1/openapi.json` to `frontend/openapi.json`
3. Run:
   ```bash
   npm run generate-client
   ```

Regenerate whenever backend API changes.

## Using a Remote API

Set `VITE_API_URL` in `frontend/.env`:

```env
VITE_API_URL=https://api.my-domain.example.com
```

## Code Structure

```
frontend/src/
+-- assets/       # Static assets
+-- client/       # Generated OpenAPI client
+-- components/   # React components
+-- hooks/        # Custom hooks
+-- routes/       # Page routes
+-- lib/          # Utility functions
```

## End-to-End Testing with Playwright

Start the backend:

```bash
docker compose up -d --wait backend
```

Run tests:

```bash
npx playwright test
```

Run in UI mode:

```bash
npx playwright test --ui
```

Clean up:

```bash
docker compose down -v
```

See [Playwright documentation](https://playwright.dev/docs/intro) for more details.

## Removing the Frontend

To create an API-only app:

1. Remove `./frontend` directory
2. Remove `frontend` service from `docker-compose.yml`
3. Remove `frontend` and `playwright` services from `docker-compose.override.yml`
