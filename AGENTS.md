# AGENTS.md

This file gives Codex and other AI coding agents the project context needed to work safely in this repository.

## Project Goal

Build a Calendly-style scheduling product with a Django REST backend, React frontend, PostgreSQL database, and Docker Compose based local development.

## Repository Layout

- `backend/`: Django project and configuration.
- `frontend/`: React + Vite application.
- `docker-compose.yml`: local development stack for PostgreSQL, Django, and React.
- `.env.example`: documented environment variables.

## Development Rules

- Keep backend and frontend code in this same repo.
- Prefer environment variables for configuration that changes by deployment environment.
- Do not commit real secrets or local `.env` files.
- Use PostgreSQL as the primary database.
- Keep changes focused and avoid broad refactors unless explicitly requested.
- Preserve user changes in the working tree.

## Backend Conventions

- Django settings live in `backend/config/settings.py`.
- Project URLs live in `backend/config/urls.py`.
- Add Django apps later when the domain implementation begins.
- Add migrations when changing models.
- Do not edit committed migration files; generate a new migration for follow-up model changes instead.
- Manage backend dependencies with `uv` and `backend/pyproject.toml`.

## Frontend Conventions

- React source code lives in `frontend/src/`.
- Prefer small, reusable components as the UI grows.

## Docker

- `docker compose up --build` should start the full local stack.
- The backend container runs migrations before starting the development server.
- The frontend container runs the Vite dev server on port `3000`.
- PostgreSQL data is stored in the `postgres_data` Docker volume mounted at `/var/lib/postgresql`.
- Backend Python dependencies are stored in the `backend_venv` Docker volume mounted at `/opt/venv`.
- Frontend Node dependencies are stored in the `frontend_node_modules` Docker volume mounted at `/app/node_modules`.
- Backend startup runs `uv sync`; frontend startup runs `npm install`. After dependency changes, still rebuild the relevant image so the image remains reproducible.
- Docker Compose passes `.env` into services with `env_file`.
- Keep environment variables minimal. Avoid duplicate sources for the same value.
- Run backend `uv` commands through Docker Compose, for example `docker compose exec backend uv lock` or `docker compose exec backend uv run python manage.py check`.

## Verification

Before handing off significant changes, run the relevant checks:

- Backend: `docker compose exec backend uv run python manage.py test`
- Frontend: `docker compose exec frontend npm run build`
- Full stack smoke test: open `http://localhost:3000` and `http://localhost:8000/admin/`
