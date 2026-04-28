# Task 08: Build Booking Details Form

## Goal

Create the invitee details form and submit bookings to the backend.

## Steps

- Build `BookingForm` with:
  - required name field
  - required email field
  - optional note field
  - submit button
- Validate required fields before submit.
- Submit the selected UTC `starts_at`, invitee details, note, and timezone.
- Show submit loading state.
- Display backend `400` messages clearly.
- On success, store the booking response and move to confirmation.

## Acceptance Criteria

- Name and email are required.
- The submitted `starts_at` is the selected UTC slot value.
- Backend `400` responses are visible to the invitee.
- Successful booking advances to the success screen.
