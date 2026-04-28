const DATE_KEY_FORMATTER_OPTIONS = {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
};

function formatDate(date, timeZone, options) {
  return new Intl.DateTimeFormat("en-US", {
    timeZone,
    ...options,
  }).format(date);
}

function getDateKeyParts(date, timeZone) {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone,
    ...DATE_KEY_FORMATTER_OPTIONS,
  }).formatToParts(date);
  const partValues = Object.fromEntries(
    parts.filter((part) => part.type !== "literal").map((part) => [part.type, part.value]),
  );

  return {
    day: partValues.day,
    month: partValues.month,
    year: partValues.year,
  };
}

function dateFromDateKey(dateKey) {
  const [year, month, day] = dateKey.split("-").map(Number);

  return new Date(Date.UTC(year, month - 1, day, 12));
}

export function getDefaultInviteeTimezone(eventTimezone) {
  try {
    return Intl.DateTimeFormat().resolvedOptions().timeZone || eventTimezone;
  } catch {
    return eventTimezone;
  }
}

export function getLocalDateKey(utcDateTime, timeZone) {
  const { year, month, day } = getDateKeyParts(new Date(utcDateTime), timeZone);

  return `${year}-${month}-${day}`;
}

export function formatSlotTimeLabel(slot, timeZone) {
  const startsAt = new Date(slot.starts_at);
  const endsAt = new Date(slot.ends_at);
  const timeOptions = {
    hour: "numeric",
    minute: "2-digit",
  };

  return `${formatDate(startsAt, timeZone, timeOptions)} - ${formatDate(
    endsAt,
    timeZone,
    timeOptions,
  )}`;
}

export function formatSelectedDateHeading(dateKey) {
  return formatDate(dateFromDateKey(dateKey), "UTC", {
    day: "numeric",
    month: "long",
    weekday: "long",
  });
}

export function formatSelectedEventDateTime(slot, timeZone) {
  const startsAt = new Date(slot.starts_at);
  const dateLabel = formatDate(startsAt, timeZone, {
    day: "numeric",
    month: "long",
    weekday: "long",
    year: "numeric",
  });

  return `${dateLabel}, ${formatSlotTimeLabel(slot, timeZone)}`;
}

export function formatTimezoneDisplay(timeZone) {
  return timeZone.replaceAll("_", " ");
}

export function groupSlotsByLocalDate(slots, timeZone) {
  return slots.reduce((groups, slot) => {
    const dateKey = getLocalDateKey(slot.starts_at, timeZone);

    return {
      ...groups,
      [dateKey]: [...(groups[dateKey] || []), slot],
    };
  }, {});
}
