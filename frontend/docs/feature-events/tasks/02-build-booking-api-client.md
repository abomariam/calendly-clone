# Task 02: Build Booking API Client

## Goal

Add a small API client for event details, availability, and booking creation.

## Steps

- Create functions for:
  - fetching event details by slug
  - fetching availability by slug and UTC range
  - creating a booking by slug
- Keep responses as plain JSON objects.
- Normalize failed requests into useful frontend errors.
- Preserve backend `400` response messages for display.
- Do not add special `409` handling.

## Acceptance Criteria

- The client supports all three public backend endpoints.
- Availability requests include `start` and `end` query parameters.
- Booking requests submit `invitee_name`, `invitee_email`, `note`, `invitee_timezone`, and UTC `starts_at`.
- Backend `400` messages are available to the UI.
