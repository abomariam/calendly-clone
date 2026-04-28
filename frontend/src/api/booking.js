import { buildApiUrl } from "./config.js";

export class ApiError extends Error {
  constructor(message, { status, detail } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.detail = detail;
  }
}

function errorMessageFromDetail(detail, fallback) {
  if (!detail) {
    return fallback;
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail.join(" ");
  }

  if (typeof detail === "object") {
    if (typeof detail.detail === "string") {
      return detail.detail;
    }

    return Object.entries(detail)
      .map(([field, messages]) => {
        const messageText = Array.isArray(messages) ? messages.join(" ") : String(messages);
        return field === "non_field_errors" ? messageText : `${field}: ${messageText}`;
      })
      .join(" ");
  }

  return fallback;
}

async function readResponseJson(response) {
  const text = await response.text();

  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function requestJson(path, options) {
  const response = await fetch(buildApiUrl(path), {
    headers: {
      Accept: "application/json",
      ...(options?.body ? { "Content-Type": "application/json" } : {}),
      ...options?.headers,
    },
    ...options,
  });
  const data = await readResponseJson(response);

  if (!response.ok) {
    throw new ApiError(errorMessageFromDetail(data, "Request failed."), {
      status: response.status,
      detail: data,
    });
  }

  return data;
}

export function fetchEventDetails(slug) {
  return requestJson(`/events/${encodeURIComponent(slug)}/`);
}

export function fetchEventAvailability(slug, { start, end }) {
  const params = new URLSearchParams({ start, end });

  return requestJson(`/events/${encodeURIComponent(slug)}/availability/?${params}`);
}

export function createBooking(
  slug,
  { invitee_name, invitee_email, note = "", invitee_timezone, starts_at },
) {
  return requestJson(`/events/${encodeURIComponent(slug)}/bookings/`, {
    method: "POST",
    body: JSON.stringify({
      invitee_name,
      invitee_email,
      note,
      invitee_timezone,
      starts_at,
    }),
  });
}
