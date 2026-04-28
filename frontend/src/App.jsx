import BookingPage from "./pages/BookingPage.jsx";

function getEventSlug(pathname) {
  const match = pathname.match(/^\/events\/([^/]+)\/?$/);

  return match ? decodeURIComponent(match[1]) : "";
}

function App() {
  const eventSlug = getEventSlug(window.location.pathname);

  if (eventSlug) {
    return <BookingPage slug={eventSlug} />;
  }

  return (
    <main className="app-shell">
      <section className="booking-placeholder">
        <p className="booking-eyebrow">Nothing to book yet</p>
        <h1>Open an event booking link to schedule a time.</h1>
        <p>Public event pages live at /events/event-slug.</p>
      </section>
    </main>
  );
}

export default App;
