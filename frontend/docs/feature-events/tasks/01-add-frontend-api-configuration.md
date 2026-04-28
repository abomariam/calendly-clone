# Task 01: Add Frontend API Configuration

## Goal

Prepare the frontend to call the Django API through a configurable base URL.

## Steps

- Add a frontend API base URL helper that reads `import.meta.env.VITE_API_BASE_URL`.
- Default the API base URL to `http://localhost:8000/api` when the env var is missing.
- Document `VITE_API_BASE_URL` in `.env.example`.
- Keep this task focused on configuration only; do not build booking UI yet.

## Acceptance Criteria

- Frontend code can construct API URLs for `/events/<slug>/`.
- Local development works without defining `VITE_API_BASE_URL`.
- `.env.example` includes the frontend API base variable.
