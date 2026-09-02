# VisionQC Frontend

This is the production React frontend for the Real-Time Industrial Defect Detection System.

## Architecture

The frontend follows a feature-based architecture to ensure scalability and maintainability:

- **`src/app/`**: Application core (Router setup, React Query provider, Environment config).
- **`src/api/`**: Centralized Axios client, interceptors (for JWTs), and TypeScript schema contracts mirroring backend Pydantic models.
- **`src/features/`**: Feature-specific modules containing their own API calls, state (Zustand), and UI components.
  - `auth/`: Login, token storage, and Role-Based Access Control (RBAC).
  - `dashboard/`: Main dashboard shell.
- **`src/components/`**: Reusable UI components (`Card`, `Button`) and layout components (`Sidebar`, `Topbar`).
- **`src/pages/`**: Global pages like `NotFound` and `Unauthorized`.

## Authentication & RBAC

The application uses JWT authentication via standard OAuth2 Password Bearer flow.
- Token is stored securely in `localStorage`.
- Axios interceptors automatically attach the token and handle `401 Unauthorized` responses gracefully.
- `RoleGuard` prevents users from accessing features they don't have permissions for, based on backend roles (`ADMIN`, `ENGINEER`, `OPERATOR`, `VIEWER`).

## Environment Setup

1. Configure `.env` with `VITE_API_BASE_URL` to point to the backend API (default is `http://localhost:8000`).

## Commands

- `npm install`: Install dependencies.
- `npm run dev`: Start development server.
- `npm run build`: Build production bundle.
- `npm run lint`: Run ESLint.
