# Task 04: Configure Django Admin

## Goal

Make event management possible through Django admin, since phase 1 has no host-facing frontend.

## Work

- Register `Event`, `EventAvailabilityRule`, and `Booking` in admin.
- Add `EventAvailabilityRule` as an inline on `Event`.
- Configure event list display for slug, duration, timezone, date range, and active status.
- Auto-generate event slugs from event names, adding a short unique suffix when needed.
- Configure booking list/search fields for event, invitee name, invitee email, and start time.

## Acceptance Criteria

- An admin user can create an event and up to 7 weekday availability rules from the event admin page.
- Admin editing exposes rule rows, not generated slots.
- Bookings are easy to search and inspect from admin.

## Suggested Verification

```bash
docker compose exec backend uv run python manage.py check
```
