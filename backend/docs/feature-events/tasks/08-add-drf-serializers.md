# Task 08: Add DRF Serializers

## Goal

Define the public API request and response shapes.

## Work

- Add an event detail serializer exposing slug, name, description, duration, timezone, and availability date range.
- Add availability query validation for `start` and `end`.
- Add availability output serialization for UTC `starts_at` and `ends_at`.
- Add booking input validation for invitee name, invitee email, note, invitee timezone, and `starts_at`.
- Add booking output serialization including booking id, event slug, invitee fields, and UTC start/end datetimes.

## Acceptance Criteria

- Serializers return UTC datetimes and do not perform invitee timezone display conversion.
- Invalid email, timezone, naive datetime, and missing required fields produce clear validation errors.
- Serializers delegate business rules like slot availability to the domain service.

## Suggested Verification

```bash
docker compose exec backend uv run python manage.py test scheduling
```
