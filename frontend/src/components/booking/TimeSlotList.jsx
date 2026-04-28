/* eslint-disable react/prop-types */
import { formatSelectedDateHeading, formatSlotTimeLabel } from "../../utils/dateTime.js";

export default function TimeSlotList({
  error,
  loading,
  onNext,
  onSlotSelect,
  selectedDate,
  selectedSlot,
  slots,
  timezone,
}) {
  if (!selectedDate) {
    return <p className="booking-muted time-slot-empty">Select a date to see available times.</p>;
  }

  if (loading) {
    return (
      <section className="time-slot-list" aria-live="polite">
        <h3>{formatSelectedDateHeading(selectedDate)}</h3>
        <p className="booking-muted">Loading available times.</p>
      </section>
    );
  }

  if (error) {
    return (
      <section className="time-slot-list" aria-live="polite">
        <h3>{formatSelectedDateHeading(selectedDate)}</h3>
        <p className="booking-error" role="alert">
          {error}
        </p>
      </section>
    );
  }

  if (slots.length === 0) {
    return (
      <section className="time-slot-list" aria-live="polite">
        <h3>{formatSelectedDateHeading(selectedDate)}</h3>
        <p className="booking-muted">No available times for this date.</p>
      </section>
    );
  }

  return (
    <section className="time-slot-list" aria-labelledby="time-slot-list-title">
      <h3 id="time-slot-list-title">{formatSelectedDateHeading(selectedDate)}</h3>
      <div className="time-slot-options">
        {slots.map((slot) => {
          const isSelected = selectedSlot?.starts_at === slot.starts_at;

          if (isSelected) {
            return (
              <div className="time-slot-selected-row" key={slot.starts_at}>
                <button className="time-slot-button time-slot-button-selected" type="button" onClick={() => onSlotSelect(slot)}>
                  {formatSlotTimeLabel(slot, timezone)}
                </button>
                <button className="time-slot-next" type="button" onClick={onNext}>
                  Next
                </button>
              </div>
            );
          }

          return (
            <button className="time-slot-button" key={slot.starts_at} type="button" onClick={() => onSlotSelect(slot)}>
              {formatSlotTimeLabel(slot, timezone)}
            </button>
          );
        })}
      </div>
    </section>
  );
}
