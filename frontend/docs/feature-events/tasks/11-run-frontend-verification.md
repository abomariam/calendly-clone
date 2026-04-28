# Task 11: Run Frontend Verification

## Goal

Verify the public booking flow works against the backend and builds successfully.

## Steps

- Run the frontend production build:

```text
docker compose exec frontend npm run build
```

- Manually test an active event slug.
- Verify event loading, availability rendering, date selection, slot selection, form validation, booking `400` error display, and success confirmation.
- Check desktop and mobile viewport behavior.

## Acceptance Criteria

- `npm run build` passes.
- Active event booking works end to end.
- Missing or inactive event shows a friendly error state.
- Booking `400` responses display useful messages.
- Submitted booking payload keeps `starts_at` as the backend UTC slot string.
