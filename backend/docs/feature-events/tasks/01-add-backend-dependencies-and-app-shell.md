# Task 01: Add Backend Dependencies And App Shell

## Goal

Prepare the backend project for the scheduling feature without adding domain behavior yet.

## Work

- Add `djangorestframework` to `backend/pyproject.toml`.
- Create a Django app named `scheduling` under `backend/`.
- Add `rest_framework` and `scheduling` to `INSTALLED_APPS` in `backend/config/settings.py`.
- Add a scheduling URL include under `/api/` from `backend/config/urls.py`.
- Add an empty `scheduling/urls.py` so later API routes have a stable home.

## Acceptance Criteria

- Django imports the new app successfully.
- `manage.py check` passes.
- No models, serializers, views, or migrations beyond the app shell are required in this task.

## Suggested Verification

```bash
docker compose exec backend uv run python manage.py check
```
