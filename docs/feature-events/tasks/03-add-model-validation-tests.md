# Task 03: Add Model Validation Tests

## Goal

Lock down model validation and database constraints before building domain services.

## Work

- Test `Event` default date behavior.
- Test invalid event timezone rejection.
- Test invalid date ranges.
- Test non-positive durations.
- Test `EventAvailabilityRule` rejects `start_time >= end_time`.
- Test duplicate weekday rules for the same event are rejected.
- Test duplicate bookings for the same `(event, starts_at)` are rejected.
- Test invalid invitee timezone rejection on `Booking`.

## Acceptance Criteria

- Tests prove the model layer rejects invalid state.
- Constraint failures are covered where model validation alone is not enough.
- These tests do not depend on DRF or public API views.

## Suggested Verification

```bash
docker compose exec backend uv run python manage.py test scheduling
```
