# Calendly Clone

A starter monorepo for a Calendly-style scheduling app with:

- Django backend
- React + Vite frontend
- PostgreSQL database
- Docker Compose for local development
- Environment-variable based configuration

## Project Structure

```text
.
|-- backend/          # Django project
|-- frontend/         # React/Vite app
|-- docker-compose.yml
|-- .env.example
|-- README.md
`-- AGENTS.md
```

## Quick Start

1. Create your local environment file:

   ```bash
   cp .env.example .env
   ```

2. Start the app:

   ```bash
   docker compose up --build
   ```

3. Open the apps:

   - Frontend: http://localhost:3000
   - Django admin: http://localhost:8000/admin/

## Backend

The Django app lives in `backend/`.

Dependencies are managed with `uv` through `backend/pyproject.toml`.

Useful commands:

```bash
docker compose exec backend uv run python manage.py migrate
docker compose exec backend uv run python manage.py createsuperuser
docker compose exec backend uv run python manage.py test
```

The backend reads configuration directly from environment variables. Docker Compose passes `.env` into the backend and database containers. PostgreSQL settings are read from the `POSTGRES_*` variables.

During local Docker development, backend dependencies live in the `backend_venv` Docker volume at `/opt/venv` so the `./backend:/app` source-code mount does not hide the virtual environment.

The backend startup command runs `uv sync` before Django starts, so the `backend_venv` volume stays aligned with `pyproject.toml`.

When backend dependencies change, rebuild the image so the image remains reproducible:

```bash
docker compose build backend
```

## Frontend

The React app lives in `frontend/`.

Useful commands:

```bash
docker compose exec frontend npm run lint
docker compose exec frontend npm run build
```

The frontend is intentionally empty for now.

During local Docker development, frontend dependencies live in the `frontend_node_modules` Docker volume at `/app/node_modules` for the same reason.

The frontend startup command runs `npm install` before Vite starts, so the `frontend_node_modules` volume stays aligned with `package.json`.

When frontend dependencies change, rebuild the image so the image remains reproducible:

```bash
docker compose build frontend
```

## Environment Files

Use `.env.example` as the source of truth for required variables. Keep real secrets in `.env` or deployment-specific secret managers, never in Git.

For future deployments, create environment-specific values for development, staging, and production while keeping variable names consistent.
