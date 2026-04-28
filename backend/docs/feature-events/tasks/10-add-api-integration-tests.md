# Task 10: Add API Integration Tests

## Goal

Cover the full public API behavior from HTTP request to database result.

## Work

- Test active event detail response.
- Test inactive and missing events return `404`.
- Test availability returns UTC slots.
- Test oversized availability windows return `400`.
- Test valid booking creates a `Booking`.
- Test invalid email, invalid timezone, and non-slot starts return `400`.
- Test duplicate booking returns `409`.

## Acceptance Criteria

- API tests cover success and failure cases for all public endpoints.
- Tests verify database side effects for booking creation.
- Tests confirm generated slots are never stored.

## Suggested Verification

```bash
docker compose exec backend uv run python manage.py test scheduling
```
