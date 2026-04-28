/* eslint-disable react/prop-types */
import { formatSelectedEventDateTime, formatTimezoneDisplay } from "../../utils/dateTime.js";

function getValidationError(formData) {
  if (!formData.inviteeName.trim()) {
    return "Enter your name.";
  }

  if (!formData.inviteeEmail.trim()) {
    return "Enter your email address.";
  }

  return "";
}

export default function BookingForm({
  error,
  formData,
  onChange,
  onSubmit,
  selectedSlot,
  submitting,
  timezone,
}) {
  const handleSubmit = (event) => {
    event.preventDefault();

    const validationError = getValidationError(formData);
    if (validationError) {
      onSubmit({ validationError });
      return;
    }

    onSubmit({ validationError: "" });
  };

  return (
    <form className="booking-form" onSubmit={handleSubmit}>
      <div className="booking-form-summary">
        <p>{formatSelectedEventDateTime(selectedSlot, timezone)}</p>
        <p>{formatTimezoneDisplay(timezone)}</p>
      </div>

      <label>
        Name
        <input
          autoComplete="name"
          name="inviteeName"
          onChange={onChange}
          required
          type="text"
          value={formData.inviteeName}
        />
      </label>

      <label>
        Email
        <input
          autoComplete="email"
          name="inviteeEmail"
          onChange={onChange}
          required
          type="email"
          value={formData.inviteeEmail}
        />
      </label>

      <label>
        Notes
        <textarea name="note" onChange={onChange} rows="4" value={formData.note} />
      </label>

      {error ? (
        <p className="booking-error" role="alert">
          {error}
        </p>
      ) : null}

      <button className="booking-submit" disabled={submitting} type="submit">
        {submitting ? "Scheduling..." : "Schedule Event"}
      </button>
    </form>
  );
}
