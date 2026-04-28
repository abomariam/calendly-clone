/* eslint-disable react/prop-types */
export default function BookingShellStatus({
  activeStep,
  availabilityLoading,
  bookingResult,
  selectedDate,
  selectedSlot,
  selectedTimezone,
}) {
  return (
    <dl className="booking-state-list" aria-label="Booking flow state">
      <div>
        <dt>Current step</dt>
        <dd>{activeStep}</dd>
      </div>
      <div>
        <dt>Invitee timezone</dt>
        <dd>{selectedTimezone || "Loading timezone"}</dd>
      </div>
      <div>
        <dt>Selected date</dt>
        <dd>{selectedDate || "Not selected"}</dd>
      </div>
      <div>
        <dt>Selected time</dt>
        <dd>{selectedSlot?.starts_at || "Not selected"}</dd>
      </div>
      <div>
        <dt>Availability</dt>
        <dd>{availabilityLoading ? "Loading" : "Not loaded yet"}</dd>
      </div>
      <div>
        <dt>Booking</dt>
        <dd>{bookingResult ? "Scheduled" : "Not submitted"}</dd>
      </div>
    </dl>
  );
}
