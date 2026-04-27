# Task 05: Build Timezone And Query Window Utilities

## Goal

Create reusable helpers for timezone validation and bounded availability query windows.

## Work

- Add a `validate_timezone(value)` helper using Python `zoneinfo`.
- Add helpers to normalize aware datetimes to UTC.
- Reject naive datetimes for API/domain inputs.
- Add a query window helper for availability requests:
  - default to a near-term window when `start` and `end` are omitted
  - reject reversed windows
  - reject windows larger than 31 days
  - clamp or reject windows outside the event availability range according to the main plan

## Acceptance Criteria

- Invalid timezone names fail consistently.
- Availability windows are always bounded before slot generation runs.
- Utilities are framework-light enough to test without making HTTP requests.

## Suggested Verification

```bash
docker compose exec backend uv run python manage.py test scheduling
```
