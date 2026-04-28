# Frontend Plan: Public Event Booking Flow

## Summary

Build the public invitee booking flow at `/events/:slug`, closely matching the provided screenshots. The UI lets an invitee view event details, pick an available date and time, enter booking details, submit the booking, and see a scheduled confirmation.

Use native CSS and a custom calendar component. This keeps the first frontend implementation small, visually controllable, and dependency-light.

Core decisions:

- Public booking only; host event management remains in Django admin.
- No new backend APIs are required.
- Use the existing public event, availability, and booking endpoints.
- Store backend slot datetimes as UTC ISO strings in frontend state.
- Convert UTC slots to the invitee timezone only for display and grouping.
- Use browser timezone as the default invitee timezone, falling back to the event timezone.
- Booking errors are handled as `400` responses with backend-provided messages.
- Use a static avatar image because the API does not expose host profile data.
- Ignore unsupported screenshot links and actions such as cookie settings, privacy links, add guests, troubleshoot, open invitation, and Calendly branding.

## API Integration

Add a small frontend API client for the existing backend contract.

### `GET /api/events/<slug>/`

Loads public event metadata.

Frontend uses:

```text
slug
name
description
duration_minutes
timezone
availability_start_date
availability_end_date
```

### `GET /api/events/<slug>/availability/?start=...&end=...`

Loads available UTC slots for the visible date range.

Frontend uses:

```text
event_timezone
duration_minutes
slots[].starts_at
slots[].ends_at
```

Rules:

- Fetch when the event loads and when the visible calendar range changes.
- Keep UTC slot strings as canonical state.
- Group slots by invitee-local calendar date after timezone conversion.
- Changing timezone should re-render existing UTC slots locally.

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

Rules:

- Submit the original selected UTC `starts_at`.
- Submit the currently selected invitee timezone.
- On `400`, show the backend message near the form or selected slot area.
- On success, render confirmation from existing event data and the booking response.

## UI Structure

Implement a single public route, `/events/:slug`.

Main components:

- `App`: parses the current path and renders the booking route or a friendly missing-route state.
- `BookingPage`: owns event data, availability data, selected date, selected slot, timezone, active step, form state, and booking result.
- `EventSummary`: left panel with avatar, event name, duration, description, selected time when available, and timezone.
- `CalendarMonth`: custom calendar grid with month navigation, available-day markers, selected date state, and disabled unavailable dates.
- `TimeSlotList`: available times for the selected date; selected time expands into selected-time button plus `Next`.
- `BookingForm`: invitee name, email, optional note, validation, submit loading state, and backend error display.
- `BookingSuccess`: scheduled confirmation using event data and booking response.

## Behavior

Initial load:

1. Parse `slug` from `/events/:slug`.
2. Fetch event metadata.
3. Initialize timezone from `Intl.DateTimeFormat().resolvedOptions().timeZone`, falling back to `event.timezone`.
4. Fetch availability for the initial visible range.
5. Render the date and time selection screen.

Slot selection:

1. Show available dates in the custom month grid.
2. When the invitee selects a date, list that date's invitee-local available times.
3. When the invitee selects a time, show the selected time and `Next`.
4. `Next` moves to the details form.

Booking submission:

1. Validate required name and email before submit.
2. Submit the original UTC `starts_at` with invitee details and selected timezone.
3. Show backend `400` messages without special `409` handling.
4. On success, show the confirmation screen.

Timezone display:

- Format calendar grouping, slot labels, selected event time, and confirmation time in invitee timezone.
- Display the selected timezone below the calendar like the screenshot.
- Do not add a full timezone picker in the first pass unless needed for testing; keep the state and formatting utilities ready for one.

## Styling

Use plain CSS in `frontend/src/styles.css` or small imported CSS files if the implementation grows.

Visual expectations:

- Centered bordered booking shell on desktop.
- Left event summary column and right workflow column.
- Compact calendar matching the screenshot rhythm.
- Blue selected date/time states.
- Clean form controls with clear focus states.
- Mobile layout stacks summary above the active booking step.
- No Tailwind or calendar library dependency in this phase.

## Test Plan

Run:

```text
docker compose exec frontend npm run build
```

Manual verification:

- Active event slug loads event details.
- Missing or inactive event shows a friendly error state.
- Available dates and slots render from the API.
- Selecting a slot reveals `Next`.
- Details form requires name and email.
- Booking `400` displays the backend message.
- Successful booking shows the confirmation screen.
- Displayed times respect invitee timezone.
- Submitted `starts_at` remains the original UTC slot value.
- Desktop and mobile layouts follow the screenshot flow closely.

## Assumptions

- Public booking only is the frontend scope for this feature.
- The backend already exists and remains unchanged.
- The first implementation can use plain React state without React Router.
- The first implementation can use native `Intl` date formatting without adding a date library.
- Static avatar presentation is acceptable for phase 1.
