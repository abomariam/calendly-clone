/* eslint-disable react/prop-types */
export default function EventDetailsPreview({ event }) {
  return (
    <section className="booking-panel" aria-labelledby="event-preview-title">
      <p className="booking-eyebrow">Public event</p>
      <h1 id="event-preview-title">{event.name}</h1>
      <p className="booking-muted">{event.duration_minutes} minutes</p>
      {event.description ? <p>{event.description}</p> : null}
      <p className="booking-muted">Event timezone: {event.timezone}</p>
    </section>
  );
}
