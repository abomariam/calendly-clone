# Task 03: Add Date And Timezone Utilities

## Goal

Centralize formatting and grouping logic for UTC slots displayed in the invitee timezone.

## Steps

- Add a helper to get the default invitee timezone from the browser, falling back to the event timezone.
- Add helpers to format:
  - slot time labels
  - selected date headings
  - selected event date and time summary
  - timezone display text
- Add a helper to group UTC slots by invitee-local calendar date.
- Keep original backend UTC `starts_at` values unchanged in state.

## Acceptance Criteria

- UTC slots can be grouped by local date for any selected timezone.
- The same slot can be displayed in a local timezone while preserving its original UTC value for booking.
- The formatting supports the screenshot-style labels such as weekday, month, day, time range, and timezone.
