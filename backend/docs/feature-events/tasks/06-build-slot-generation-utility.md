# Task 06: Build Slot Generation Utility

## Goal

Generate available UTC booking slots from event-local weekly rules without storing generated slots.

## Work

- Add `generate_available_slots(event, start_utc, end_utc)`.
- Interpret `EventAvailabilityRule` rows in the event timezone.
- Walk event-local dates inside the requested UTC window.
- Generate slots by stepping forward by `event.duration_minutes`.
- Keep slots where `slot_start + duration <= rule_end`.
- Exclude slots outside the event date range.
- Query existing bookings for the event/window and exclude booked starts.
- Return UTC `starts_at` and `ends_at` values.

## Acceptance Criteria

- `09:00-11:00` with 30-minute duration returns 4 slots.
- `09:00-11:00` with 45-minute duration returns `09:00` and `09:45`.
- 24/7 weekly availability generates slots on demand without creating slot records.
- Already booked slots are excluded.

## Suggested Verification

```bash
docker compose exec backend uv run python manage.py test scheduling
```
