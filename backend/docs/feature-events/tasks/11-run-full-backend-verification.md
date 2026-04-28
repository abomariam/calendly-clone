# Task 11: Run Full Backend Verification

## Goal

Confirm the completed backend feature works as a coherent slice.

## Work

- Run migrations from the current database state.
- Run the full backend test suite.
- Run Django system checks.
- Smoke-test Django admin manually or with a browser:
  - create an event
  - add weekday availability rules
  - inspect bookings
- Optionally call the public endpoints with a sample active event.

## Acceptance Criteria

- Migrations apply cleanly.
- Full backend tests pass.
- Admin can manage events and bookings.
- Public APIs expose event details, availability, and booking creation.

## Suggested Verification

```bash
docker compose exec backend uv run python manage.py migrate
docker compose exec backend uv run python manage.py test
docker compose exec backend uv run python manage.py check
```
