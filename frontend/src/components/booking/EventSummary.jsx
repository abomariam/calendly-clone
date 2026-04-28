/* eslint-disable react/prop-types */
import hostAvatarUrl from "../../assets/host-avatar.svg";
import { formatSelectedEventDateTime, formatTimezoneDisplay } from "../../utils/dateTime.js";

export default function EventSummary({ activeStep, event, onBack, selectedSlot, selectedTimezone }) {
  const showBackButton = activeStep === "details";
  const selectedTimeLabel =
    selectedSlot && selectedTimezone ? formatSelectedEventDateTime(selectedSlot, selectedTimezone) : "";

  return (
    <section className="booking-panel event-summary" aria-labelledby="event-summary-title">
      {showBackButton ? (
        <button className="event-summary-back" type="button" onClick={onBack} aria-label="Back to date and time">
          Back
        </button>
      ) : null}

      <img className="event-summary-avatar" src={hostAvatarUrl} alt="" />
      <p className="event-summary-host">Calendly Clone</p>
      <h1 id="event-summary-title">{event.name}</h1>

      <div className="event-summary-meta" aria-label="Event details">
        <p>{event.duration_minutes} minutes</p>
        {selectedTimeLabel ? <p>{selectedTimeLabel}</p> : null}
        {selectedTimezone ? <p>{formatTimezoneDisplay(selectedTimezone)}</p> : null}
      </div>

      {event.description ? <p className="event-summary-description">{event.description}</p> : null}
    </section>
  );
}
