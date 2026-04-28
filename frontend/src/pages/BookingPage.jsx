/* eslint-disable react/prop-types */
import { useEffect, useState } from "react";

import { fetchEventDetails } from "../api/booking.js";
import BookingShellStatus from "../components/booking/BookingShellStatus.jsx";
import EventDetailsPreview from "../components/booking/EventDetailsPreview.jsx";
import { getDefaultInviteeTimezone } from "../utils/dateTime.js";

export default function BookingPage({ slug }) {
  const [eventRequest, setEventRequest] = useState({
    error: "",
    event: null,
    loading: true,
    slug,
  });
  const [availabilityLoading] = useState(false);
  const [availabilityError] = useState("");
  const [selectedDate] = useState("");
  const [selectedSlot] = useState(null);
  const [selectedTimezone, setSelectedTimezone] = useState("");
  const [activeStep] = useState("date-time");
  const [bookingResult] = useState(null);

  useEffect(() => {
    let isCurrent = true;

    fetchEventDetails(slug)
      .then((eventDetails) => {
        if (!isCurrent) {
          return;
        }

        setEventRequest({
          error: "",
          event: eventDetails,
          loading: false,
          slug,
        });
        setSelectedTimezone(getDefaultInviteeTimezone(eventDetails.timezone));
      })
      .catch((error) => {
        if (!isCurrent) {
          return;
        }

        setEventRequest({
          error: error.message || "We could not load this event.",
          event: null,
          loading: false,
          slug,
        });
      });

    return () => {
      isCurrent = false;
    };
  }, [slug]);

  const eventLoading = eventRequest.slug !== slug || eventRequest.loading;
  const eventError = eventRequest.slug === slug ? eventRequest.error : "";
  const event = eventRequest.slug === slug ? eventRequest.event : null;

  if (eventLoading || (!event && !eventError)) {
    return (
      <main className="app-shell">
        <section className="booking-placeholder" aria-live="polite">
          <p className="booking-eyebrow">Loading event</p>
          <h1>Getting this booking page ready</h1>
        </section>
      </main>
    );
  }

  if (eventError) {
    return (
      <main className="app-shell">
        <section className="booking-placeholder" role="alert">
          <p className="booking-eyebrow">Event unavailable</p>
          <h1>We could not load this event</h1>
          <p>{eventError}</p>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <div className="booking-shell">
        <EventDetailsPreview event={event} />
        <section className="booking-panel" aria-labelledby="booking-shell-title">
          <p className="booking-eyebrow">Booking flow</p>
          <h2 id="booking-shell-title">Choose a date and time</h2>
          <p className="booking-muted">Calendar and availability controls land in the next steps.</p>
          {availabilityError ? <p role="alert">{availabilityError}</p> : null}
          <BookingShellStatus
            activeStep={activeStep}
            availabilityLoading={availabilityLoading}
            bookingResult={bookingResult}
            selectedDate={selectedDate}
            selectedSlot={selectedSlot}
            selectedTimezone={selectedTimezone}
          />
        </section>
      </div>
    </main>
  );
}
