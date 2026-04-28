/* eslint-disable react/prop-types */
const WEEKDAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function getMonthStart(date) {
  return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), 1));
}

function addMonths(date, amount) {
  return new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth() + amount, 1));
}

function getDateKey(date) {
  const year = date.getUTCFullYear();
  const month = String(date.getUTCMonth() + 1).padStart(2, "0");
  const day = String(date.getUTCDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
}

function getMonthDays(monthDate) {
  const monthStart = getMonthStart(monthDate);
  const daysInMonth = new Date(
    Date.UTC(monthStart.getUTCFullYear(), monthStart.getUTCMonth() + 1, 0),
  ).getUTCDate();
  const leadingBlankCount = monthStart.getUTCDay();
  const cells = Array.from({ length: leadingBlankCount }, (_, index) => ({
    key: `blank-${index}`,
    type: "blank",
  }));

  for (let day = 1; day <= daysInMonth; day += 1) {
    const date = new Date(Date.UTC(monthStart.getUTCFullYear(), monthStart.getUTCMonth(), day));

    cells.push({
      dateKey: getDateKey(date),
      day,
      key: getDateKey(date),
      type: "day",
    });
  }

  return cells;
}

function formatMonthLabel(monthDate) {
  return new Intl.DateTimeFormat("en-US", {
    month: "long",
    timeZone: "UTC",
    year: "numeric",
  }).format(monthDate);
}

export default function CalendarMonth({ availableDates, monthDate, onDateSelect, onMonthChange, selectedDate }) {
  const availableDateSet = new Set(availableDates);
  const monthStart = getMonthStart(monthDate);
  const cells = getMonthDays(monthStart);

  return (
    <div className="calendar-month">
      <div className="calendar-month-header">
        <h3>{formatMonthLabel(monthStart)}</h3>
        <div className="calendar-month-controls" aria-label="Calendar month controls">
          <button
            type="button"
            onClick={() => onMonthChange(addMonths(monthStart, -1))}
            aria-label="Previous month"
          >
            {"<"}
          </button>
          <button type="button" onClick={() => onMonthChange(addMonths(monthStart, 1))} aria-label="Next month">
            {">"}
          </button>
        </div>
      </div>

      <div className="calendar-grid" role="grid" aria-label={formatMonthLabel(monthStart)}>
        {WEEKDAY_LABELS.map((label) => (
          <div className="calendar-weekday" key={label} role="columnheader">
            {label}
          </div>
        ))}

        {cells.map((cell) => {
          if (cell.type === "blank") {
            return <div className="calendar-day calendar-day-blank" key={cell.key} />;
          }

          const isAvailable = availableDateSet.has(cell.dateKey);
          const isSelected = selectedDate === cell.dateKey;

          return (
            <button
              className={[
                "calendar-day",
                isAvailable ? "calendar-day-available" : "calendar-day-unavailable",
                isSelected ? "calendar-day-selected" : "",
              ]
                .filter(Boolean)
                .join(" ")}
              disabled={!isAvailable}
              key={cell.key}
              onClick={() => onDateSelect(cell.dateKey)}
              type="button"
            >
              <span>{cell.day}</span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
