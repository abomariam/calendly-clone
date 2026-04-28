/* eslint-disable react/prop-types */
import { useEffect, useMemo, useState } from "react";

import { createBooking, fetchEventAvailability, fetchEventDetails } from "../api/booking.js";
import BookingForm from "../components/booking/BookingForm.jsx";
import BookingSuccess from "../components/booking/BookingSuccess.jsx";
import CalendarMonth from "../components/booking/CalendarMonth.jsx";
import EventSummary from "../components/booking/EventSummary.jsx";
import TimeSlotList from "../components/booking/TimeSlotList.jsx";
import { formatTimezoneDisplay, getDefaultInviteeTimezone, groupSlotsByLocalDate } from "../utils/dateTime.js";

function getMonthStart(date = new Date()) {
  return new Date(Date.UTC(date.getFullYear(), date.getMonth(), 1));
}

function getMonthStartFromDateKey(dateKey) {
  const [year, month] = dateKey.split("-").map(Number);

  return new Date(Date.UTC(year, month - 1, 1));
}

function addMonths(date, amount) {
  return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + amount, 1));
}

function getAvailabilityRange(monthDate) {
  const start = new Date(Date.UTC(monthDate.getUTCFullYear(), monthDate.getUTCMonth(), 1));
  const end = addMonths(start, 1);

  return {
    end: end.toISOString(),
    key: `${start.toISOString()}_${end.toISOString()}`,
    start: start.toISOString(),
  };
}

export default function BookingPage({ slug }) {
  const [eventRequest, setEventRequest] = useState({
    error: "",
    event: null,
    loading: true,
    slug,
  });
  const [availabilityRequest, setAvailabilityRequest] = useState({
    error: "",
    key: "",
    slots: [],
  });
  const [visibleMonth, setVisibleMonth] = useState(() => getMonthStart());
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [selectedTimezone, setSelectedTimezone] = useState("");
  const [activeStep, setActiveStep] = useState("date-time");
  const [bookingResult, setBookingResult] = useState(null);
  const [bookingFormData, setBookingFormData] = useState({
    inviteeEmail: "",
    inviteeName: "",
    note: "",
  });
  const [bookingError, setBookingError] = useState("");
  const [bookingSubmitting, setBookingSubmitting] = useState(false);

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
        setVisibleMonth(getMonthStartFromDateKey(eventDetails.availability_start_date));
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
  const availabilityRange = useMemo(() => getAvailabilityRange(visibleMonth), [visibleMonth]);

  useEffect(() => {
    if (!event) {
      return undefined;
    }

    let isCurrent = true;

    fetchEventAvailability(slug, availabilityRange)
      .then((availability) => {
        if (!isCurrent) {
          return;
        }

        setAvailabilityRequest({
          error: "",
          key: availabilityRange.key,
          slots: availability.slots,
        });
      })
      .catch((error) => {
        if (!isCurrent) {
          return;
        }

        setAvailabilityRequest({
          error: error.message || "We could not load availability.",
          key: availabilityRange.key,
          slots: [],
        });
      });

    return () => {
      isCurrent = false;
    };
  }, [availabilityRange, event, slug]);

  const availabilityLoading = Boolean(event) && availabilityRequest.key !== availabilityRange.key;
  const availabilityError = availabilityRequest.key === availabilityRange.key ? availabilityRequest.error : "";
  const slotsByDate = useMemo(() => {
    if (!selectedTimezone || availabilityRequest.key !== availabilityRange.key) {
      return {};
    }

    return groupSlotsByLocalDate(availabilityRequest.slots, selectedTimezone);
  }, [availabilityRange.key, availabilityRequest, selectedTimezone]);
  const availableDates = useMemo(() => Object.keys(slotsByDate).sort(), [slotsByDate]);
  const selectedDateSlots = selectedDate ? slotsByDate[selectedDate] || [] : [];

  const handleDateSelect = (dateKey) => {
    setSelectedDate(dateKey);
    setSelectedSlot(null);
    setBookingError("");
  };
  const handleMonthChange = (monthDate) => {
    setVisibleMonth(monthDate);
    setSelectedDate("");
    setSelectedSlot(null);
    setBookingError("");
  };
  const handleBookingFormChange = (event) => {
    const { name, value } = event.target;

    setBookingFormData((currentFormData) => ({
      ...currentFormData,
      [name]: value,
    }));
    setBookingError("");
  };
  const handleBookingSubmit = ({ validationError }) => {
    if (validationError) {
      setBookingError(validationError);
      return;
    }

    if (!selectedSlot) {
      setBookingError("Select a time before scheduling.");
      return;
    }

    setBookingError("");
    setBookingSubmitting(true);

    createBooking(slug, {
      invitee_email: bookingFormData.inviteeEmail,
      invitee_name: bookingFormData.inviteeName,
      invitee_timezone: selectedTimezone,
      note: bookingFormData.note,
      starts_at: selectedSlot.starts_at,
    })
      .then((booking) => {
        setBookingResult(booking);
        setActiveStep("success");
      })
      .catch((error) => {
        setBookingError(error.message || "We could not schedule this event.");
      })
      .finally(() => {
        setBookingSubmitting(false);
      });
  };

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
        <EventSummary
          activeStep={activeStep}
          event={event}
          onBack={() => setActiveStep("date-time")}
          selectedSlot={selectedSlot}
          selectedTimezone={selectedTimezone}
        />
        <section className="booking-panel" aria-labelledby="booking-shell-title">
          <p className="booking-eyebrow">Booking flow</p>
          {activeStep === "date-time" ? (
            <>
              <h2 id="booking-shell-title">Choose a date and time</h2>
              <CalendarMonth
                availableDates={availableDates}
                monthDate={visibleMonth}
                onDateSelect={handleDateSelect}
                onMonthChange={handleMonthChange}
                selectedDate={selectedDate}
              />
              <p className="booking-muted timezone-display">{formatTimezoneDisplay(selectedTimezone)}</p>
              <TimeSlotList
                error={availabilityError}
                loading={availabilityLoading}
                onNext={() => setActiveStep("details")}
                onSlotSelect={setSelectedSlot}
                selectedDate={selectedDate}
                selectedSlot={selectedSlot}
                slots={selectedDateSlots}
                timezone={selectedTimezone}
              />
            </>
          ) : null}
          {activeStep === "details" ? (
            <>
              <h2 id="booking-shell-title">Enter details</h2>
              <BookingForm
                error={bookingError}
                formData={bookingFormData}
                onChange={handleBookingFormChange}
                onSubmit={handleBookingSubmit}
                selectedSlot={selectedSlot}
                submitting={bookingSubmitting}
                timezone={selectedTimezone}
              />
            </>
          ) : null}
          {activeStep === "success" && bookingResult ? (
            <BookingSuccess booking={bookingResult} event={event} timezone={selectedTimezone} />
          ) : null}
        </section>
      </div>
    </main>
  );
}
