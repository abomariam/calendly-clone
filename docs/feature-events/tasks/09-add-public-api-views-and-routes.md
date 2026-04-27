# Task 09: Add Public API Views And Routes

## Goal

Expose the public event and booking API endpoints needed by the future frontend.

## Work

- Add `GET /api/events/<slug>/` for public event details.
- Add `GET /api/events/<slug>/availability/` for available UTC slots.
- Add `POST /api/events/<slug>/bookings/` for booking creation.
- Return `404` for missing or inactive events.
- Return `400` for invalid request data.
- Return `409` when the requested slot was already booked.
- Keep event management out of the public API.

## Acceptance Criteria

- Public endpoints match the response shapes in `docs/feature-events/plan.md`.
- Inactive events are hidden from all public endpoints.
- Availability responses contain UTC slot datetimes only.

## Suggested Verification

```bash
docker compose exec backend uv run python manage.py test scheduling
```
