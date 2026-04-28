# Task 07: Load Availability And Render Time Slots

## Goal

Fetch availability for the visible range and display slots for the selected date.

## Steps

- Fetch availability after event data loads and whenever the visible calendar range changes.
- Store returned slots as UTC ISO strings.
- Group slots by invitee-local date using the timezone utilities.
- Build `TimeSlotList` for the selected date.
- Show loading, empty, and error states.
- When a slot is selected, show the selected slot button plus `Next`.

## Acceptance Criteria

- Available dates come from real backend slots.
- Selecting a date shows only that date's invitee-local slots.
- Selecting a slot reveals the `Next` action.
- Timezone changes re-render existing slots without losing UTC booking values.
