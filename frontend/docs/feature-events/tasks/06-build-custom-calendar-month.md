# Task 06: Build Custom Calendar Month

## Goal

Build the custom month calendar used for selecting available dates.

## Steps

- Render a one-month grid with weekday labels.
- Add previous and next month controls.
- Highlight the selected date.
- Mark dates that have available slots.
- Disable or visually de-emphasize dates with no available slots.
- Keep the component controlled by props for month, selected date, available dates, and callbacks.

## Acceptance Criteria

- The calendar layout closely matches the screenshots.
- Available dates are clearly selectable.
- Selecting a date updates the parent page state.
- Month navigation triggers the parent to load the relevant availability range.
