# Backend Plan: Stripped-Down Calendly Clone

## Summary

Build a `scheduling` Django app for event booking. Event management will happen through Django admin only; public booking flows will use Django REST Framework APIs.

The backend will store availability as weekly rules, not precomputed slots. Bookable slots are generated on demand from the event duration, date range, timezone, and existing bookings.

Core decisions:

- No register/login flow.
- Events are not linked to users.
- Every event behaves like a one-on-one meeting.
- Django admin is the only event management UI.
- Public APIs expose event details, available UTC slots, and booking creation.
- Frontend handles invitee timezone display/conversion.
- Backend stores all booking datetimes in UTC.

## Data Model

Add a new Django app: `scheduling`.

### `Event`

Stores the public event definition.

Fields:

```text
id
name
slug
description
duration_minutes
availability_start_date
availability_end_date
timezone
is_active
created_at
updated_at
```

Rules:

- `slug` is unique and used in public booking URLs.
- `description` replaces Calendly's location field.
- `duration_minutes` defaults to `30`.
- `availability_start_date` defaults to today.
- `availability_end_date` defaults to today + 60 days.
- `timezone` stores an IANA timezone like `Africa/Cairo`.
- `is_active=False` hides the event from public APIs.

### `EventAvailabilityRule`

Stores weekly availability rules, not generated slots.

Fields:

```text
id
event
weekday
start_time
end_time
```

Rules:

- `weekday` is `0-6`, Monday through Sunday.
- One row represents one local availability window for that weekday.
- Phase 1 supports one rule per weekday.
- Unique constraint: `(event, weekday)`.
- `start_time < end_time`.

Example 24/7 event:

```text
Monday     00:00-23:59
Tuesday    00:00-23:59
Wednesday  00:00-23:59
Thursday   00:00-23:59
Friday     00:00-23:59
Saturday   00:00-23:59
Sunday     00:00-23:59
```

This is 7 database rows, not 336 generated 30-minute slots.

### `Booking`

Stores confirmed reservations.

Fields:

```text
id
event
invitee_name
invitee_email
note
invitee_timezone
starts_at
ends_at
created_at
```

Rules:

- `starts_at` and `ends_at` are stored in UTC.
- `invitee_timezone` stores the timezone the invitee selected when booking.
- Unique constraint: `(event, starts_at)`.
- `ends_at = starts_at + event.duration_minutes`.

Indexes:

```text
Event.slug unique index
EventAvailabilityRule(event, weekday)
Booking(event, starts_at)
Booking(event, starts_at) unique
```

## Availability And Booking Logic

Availability is interpreted in the event host timezone.

Slot generation:

1. Load event and weekly availability rules.
2. Pick a bounded query window, usually 1 calendar month.
3. Convert the query window into event-local dates.
4. For each local date, find its weekday rule.
5. Combine local date + `start_time` / `end_time`.
6. Step forward by `duration_minutes`.
7. Keep slots where `slot_start + duration <= rule_end`.
8. Convert generated slot start/end to UTC.
9. Exclude already-booked UTC starts.
10. Return UTC slots to the frontend.

Example:

```text
Event timezone: Africa/Cairo
Duration: 30 minutes
Monday rule: 09:00-11:00

Generated local starts:
09:00
09:30
10:00
10:30

Returned API starts:
UTC ISO datetimes
```

Booking creation:

1. Receive `starts_at` as a UTC datetime.
2. Validate invitee name, email, note, and timezone.
3. Confirm `starts_at` exactly matches a generated available slot.
4. Confirm the slot is not in the past.
5. Create booking inside `transaction.atomic()`.
6. If the unique constraint fails, return `409 Conflict`.

Performance approach:

- Do not store possible slots.
- Generate candidate slots on demand.
- Query bookings only for the event and requested window.
- Cap availability requests to a practical range, such as 31 days.
- PostgreSQL will handle large booking counts well with `(event_id, starts_at)` indexing.

## Timezone Rules

Backend canonical data:

- Event availability rules are stored in the event timezone.
- Booking datetimes are stored in UTC.
- API availability responses return UTC datetimes.
- Invitee timezone is saved only as booking metadata.

The frontend should convert UTC slots into the selected invitee timezone for display.

Availability response example:

```json
{
  "event_timezone": "Africa/Cairo",
  "slots": [
    {
      "starts_at": "2026-05-04T07:00:00Z",
      "ends_at": "2026-05-04T07:30:00Z"
    }
  ]
}
```

When the invitee switches timezone, the frontend should usually re-render existing UTC slots locally instead of calling the API again.

The frontend should call the API again only when:

- the visible date range changes,
- the selected range is not already loaded,
- or the UI needs adjacent slots because timezone conversion moved slots across local day boundaries.

Use Python `zoneinfo.ZoneInfo` on the backend. Invalid or unknown timezone names should return validation errors.

## Admin

Use Django admin for phase 1 event management.

Admin setup:

- Register `Event`.
- Register `Booking`.
- Add `EventAvailabilityRule` as an inline on `Event`.
- Show event slug, duration, timezone, date range, active status.
- Auto-generate slug from name, with a short random suffix if needed.
- Make bookings searchable by invitee name, invitee email, and event name.
- Bookings may be editable in admin, but public APIs only create bookings.

Admin editing should be straightforward because the host edits up to 7 weekday rules, not thousands of generated slots.

## Public APIs

Use Django REST Framework.

### `GET /api/events/<slug>/`

Returns public event metadata.

Example:

```json
{
  "slug": "intro-call-a8f3k2",
  "name": "Intro Call",
  "description": "We will discuss the project scope.",
  "duration_minutes": 30,
  "timezone": "Africa/Cairo",
  "availability_start_date": "2026-04-27",
  "availability_end_date": "2026-06-26"
}
```

### `GET /api/events/<slug>/availability/?start=2026-05-01T00:00:00Z&end=2026-06-01T00:00:00Z`

Returns available UTC slots.

Rules:

- `start` and `end` are UTC datetimes.
- If omitted, default to a near-term window, such as today through 31 days from today.
- Reject ranges longer than the configured maximum, such as 31 days.
- Return only slots within the event's availability date range.
- Return only unbooked slots.
- Return `404` for missing or inactive events.

Example:

```json
{
  "event_timezone": "Africa/Cairo",
  "duration_minutes": 30,
  "slots": [
    {
      "starts_at": "2026-05-04T07:00:00Z",
      "ends_at": "2026-05-04T07:30:00Z"
    }
  ]
}
```

### `POST /api/events/<slug>/bookings/`

Creates a booking.

Request:

```json
{
  "invitee_name": "Mona Hassan",
  "invitee_email": "mona@example.com",
  "note": "I want to discuss pricing.",
  "invitee_timezone": "Europe/London",
  "starts_at": "2026-05-04T07:00:00Z"
}
```

Success response:

```json
{
  "id": 42,
  "event": "intro-call-a8f3k2",
  "invitee_name": "Mona Hassan",
  "invitee_email": "mona@example.com",
  "note": "I want to discuss pricing.",
  "invitee_timezone": "Europe/London",
  "starts_at": "2026-05-04T07:00:00Z",
  "ends_at": "2026-05-04T07:30:00Z"
}
```

Status codes:

```text
201 Created
400 Invalid request or invalid slot
404 Event not found or inactive
409 Slot already booked
```

## Utilities

Add scheduling utilities for reusable domain logic:

```text
validate_timezone(value)
get_event_query_window(event, start, end)
generate_available_slots(event, start_utc, end_utc)
is_bookable_slot(event, starts_at_utc)
create_booking(event, validated_payload)
```

Keep slot generation outside serializers/views so it is easy to test.

## Validations And Edge Cases

Event validations:

- Name is required.
- Duration must be positive.
- End date must be on or after start date.
- Timezone must be valid.
- Availability rule start time must be before end time.
- Availability rule must be long enough for at least one slot.
- Duplicate weekday rules are rejected.

Booking validations:

- Invitee name is required.
- Invitee email is required and must be valid.
- Invitee timezone is required and must be valid.
- `starts_at` must be timezone-aware.
- `starts_at` must be in UTC or normalized to UTC.
- Slot must not be in the past.
- Slot must exactly match a generated slot start.
- Slot must fall inside the event date range.
- Slot must not already be booked.

Edge cases:

- Event end date is inclusive in the event timezone.
- A slot ending exactly at the availability end time is valid.
- A slot that would end after the availability end time is invalid.
- If the event has no availability rules, availability returns an empty slot list.
- If two invitees book the same slot concurrently, one succeeds and one receives `409`.
- DST transitions are handled by generating local event times with `zoneinfo` and storing final booking times in UTC.

## Test Plan

Model tests:

- Event date defaults are applied correctly.
- Invalid event timezone is rejected.
- Invalid invitee timezone is rejected.
- Availability rule with `start_time >= end_time` is rejected.
- Duplicate weekday rule is rejected.
- Duplicate booking for the same event/start is rejected.

Slot generation tests:

- `09:00-11:00` with 30-minute duration returns 4 slots.
- `09:00-11:00` with 45-minute duration returns `09:00` and `09:45`.
- Booked slots are excluded.
- Slots before the event start date are excluded.
- Slots after the event end date are excluded.
- 24/7 weekly rules generate expected slots without storing them.

API tests:

- Event detail endpoint returns active event metadata.
- Inactive event returns `404`.
- Availability endpoint returns UTC slots.
- Availability endpoint rejects too-large query windows.
- Booking endpoint creates a valid booking.
- Booking endpoint rejects invalid email.
- Booking endpoint rejects invalid timezone.
- Booking endpoint rejects non-slot times.
- Booking endpoint rejects already-booked slots with `409`.

## Assumptions

- Event CRUD is Django admin only.
- DRF will be added as a backend dependency.
- Phase 1 supports one availability range per weekday.
- Generated slots are never stored in the database.
- Public APIs return UTC datetimes.
- Frontend owns invitee timezone display and timezone switching.
- No emails, notifications, cancellation, rescheduling, buffers, recurring exceptions, or payment logic in phase 1.
