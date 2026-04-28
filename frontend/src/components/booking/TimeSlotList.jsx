/* eslint-disable react/prop-types */
import { useEffect, useState } from "react";
import {
  formatSelectedDateHeading,
  formatSlotStartTimeLabel,
} from "../../utils/dateTime.js";

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
  const selectedSlotStart = selectedSlot?.starts_at || "";
  const [departingSlotStart, setDepartingSlotStart] = useState("");

  useEffect(() => {
    if (!departingSlotStart) {
      return undefined;
    }

    const timeoutId = window.setTimeout(() => {
      setDepartingSlotStart((currentSlotStart) => (currentSlotStart === departingSlotStart ? "" : currentSlotStart));
    }, 280);

    return () => window.clearTimeout(timeoutId);
  }, [departingSlotStart]);

  const handleSlotSelect = (slot, isSelected) => {
    if (isSelected) {
      setDepartingSlotStart(slot.starts_at);
      onSlotSelect(null);
      return;
    }

    if (selectedSlotStart) {
      setDepartingSlotStart(selectedSlotStart);
    }

    onSlotSelect(slot);
  };

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
          const isSelected = selectedSlotStart === slot.starts_at;
          const isDeparting = !isSelected && departingSlotStart === slot.starts_at;

          if (isSelected || isDeparting) {
            const selectedRowClassName = [
              "time-slot-selected-row",
              isDeparting ? "time-slot-selected-row-exiting" : "",
            ]
              .filter(Boolean)
              .join(" ");

            return (
              <div
                className={selectedRowClassName}
                key={slot.starts_at}
                onAnimationEnd={(event) => {
                  if (event.currentTarget === event.target && isDeparting) {
                    setDepartingSlotStart((currentSlotStart) =>
                      currentSlotStart === slot.starts_at ? "" : currentSlotStart,
                    );
                  }
                }}
              >
                <button
                  aria-disabled={isDeparting || undefined}
                  aria-pressed={isSelected}
                  className="time-slot-button time-slot-button-selected"
                  tabIndex={isDeparting ? -1 : undefined}
                  type="button"
                  onClick={() => {
                    if (!isDeparting) {
                      handleSlotSelect(slot, isSelected);
                    }
                  }}
                >
                  {formatSlotStartTimeLabel(slot, timezone)}
                </button>
                <button
                  aria-disabled={isDeparting || undefined}
                  className="time-slot-next"
                  tabIndex={isDeparting ? -1 : undefined}
                  type="button"
                  onClick={() => {
                    if (!isDeparting) {
                      onNext();
                    }
                  }}
                >
                  Next
                </button>
              </div>
            );
          }

          return (
            <button
              className="time-slot-button"
              key={slot.starts_at}
              type="button"
              onClick={() => handleSlotSelect(slot, isSelected)}
            >
              {formatSlotStartTimeLabel(slot, timezone)}
            </button>
          );
        })}
      </div>
    </section>
  );
}
