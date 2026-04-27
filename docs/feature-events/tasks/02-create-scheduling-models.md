# Task 02: Create Scheduling Models

## Goal

Add the database schema for events, weekly availability rules, and confirmed bookings.

## Work

- Add `Event` with `name`, `slug`, `description`, `duration_minutes`, `availability_start_date`, `availability_end_date`, `timezone`, `is_active`, `created_at`, and `updated_at`.
- Add `EventAvailabilityRule` with `event`, `weekday`, `start_time`, and `end_time`.
- Add `Booking` with `event`, `invitee_name`, `invitee_email`, `note`, `invitee_timezone`, `starts_at`, `ends_at`, and `created_at`.
- Add constraints and indexes:
  - unique `Event.slug`
  - unique `(event, weekday)` for `EventAvailabilityRule`
  - indexed and unique `(event, starts_at)` for `Booking`
- Add model-level validation for positive duration, valid date ranges, valid timezones, and valid availability windows.
- Generate the initial scheduling migration.

## Acceptance Criteria

- Availability is stored as weekly rules only, never as generated slot rows.
- Migrations apply cleanly.
- The schema supports the public APIs described in `docs/feature-events/plan.md`.

## Suggested Verification

```bash
docker compose exec backend uv run python manage.py makemigrations --check
docker compose exec backend uv run python manage.py migrate
```
