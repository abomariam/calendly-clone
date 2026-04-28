# Task 07: Build Booking Creation Service

## Goal

Centralize booking creation so API views do not duplicate booking rules.

## Work

- Add `is_bookable_slot(event, starts_at_utc)`.
- Add `create_booking(event, validated_payload)`.
- Require requested `starts_at` to exactly match a generated available slot.
- Reject past slots.
- Calculate `ends_at` from the event duration.
- Save inside `transaction.atomic()`.
- Convert duplicate `(event, starts_at)` integrity errors into a domain error that API views can return as `409 Conflict`.

## Acceptance Criteria

- Valid requests create bookings with correct UTC start/end datetimes.
- Invalid or non-slot starts are rejected.
- Past slots are rejected.
- Concurrent duplicate booking attempts are protected by the database uniqueness constraint.

## Suggested Verification

```bash
docker compose exec backend uv run python manage.py test scheduling
```
