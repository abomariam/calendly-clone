# Task 04: Create Route And Booking Page Shell

## Goal

Add the `/events/:slug` entry point and the main booking page state container.

## Steps

- Parse `/events/:slug` from the browser location in `App`.
- Render a friendly missing-route state when no event slug is present.
- Create `BookingPage` to own:
  - event loading state
  - availability loading state
  - selected date
  - selected slot
  - selected timezone
  - active step
  - booking result
- Fetch event details on initial page load.
- Initialize invitee timezone after event details load.

## Acceptance Criteria

- Visiting `/events/<slug>` renders the booking page.
- Event loading and error states are visible.
- The page can hold all booking flow state without prop drilling becoming messy.
