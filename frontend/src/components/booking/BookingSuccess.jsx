/* eslint-disable react/prop-types */
import { formatSelectedEventDateTime, formatTimezoneDisplay } from "../../utils/dateTime.js";

export default function BookingSuccess({ booking, event, timezone }) {
  const bookingSlot = {
    ends_at: booking.ends_at,
    starts_at: booking.starts_at,
  };

  return (
    <section className="booking-success" aria-labelledby="booking-success-title" aria-live="polite">
      <div className="booking-success-icon" aria-hidden="true">
        OK
      </div>
      <p className="booking-eyebrow">Scheduled</p>
      <h2 id="booking-success-title">You are scheduled</h2>
      <p className="booking-muted">A calendar event has been created for this booking.</p>

      <dl className="booking-success-details" aria-label="Booking details">
        <div>
          <dt>Event</dt>
          <dd>{event.name}</dd>
        </div>
        <div>
          <dt>When</dt>
          <dd>{formatSelectedEventDateTime(bookingSlot, timezone)}</dd>
        </div>
        <div>
          <dt>Timezone</dt>
          <dd>{formatTimezoneDisplay(timezone)}</dd>
        </div>
        <div>
          <dt>Invitee</dt>
          <dd>
            {booking.invitee_name}
            <span>{booking.invitee_email}</span>
          </dd>
        </div>
        {booking.note ? (
          <div>
            <dt>Notes</dt>
            <dd>{booking.note}</dd>
          </div>
        ) : null}
      </dl>

      {event.description ? <p className="booking-success-description">{event.description}</p> : null}
    </section>
  );
}
