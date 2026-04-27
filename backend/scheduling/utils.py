from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.core.exceptions import ValidationError
from django.utils import timezone

MAX_AVAILABILITY_WINDOW_DAYS = 31


def default_availability_start_date():
    return timezone.localdate()


def default_availability_end_date():
    return timezone.localdate() + timedelta(days=60)


def validate_timezone(value):
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, TypeError, ValueError):
        raise ValidationError("%(value)s is not a valid IANA timezone.", params={"value": value})


def normalize_to_utc(value):
    if timezone.is_naive(value):
        raise ValidationError("Datetime must be timezone-aware.")

    return value.astimezone(timezone.UTC)


def get_event_query_window(event, start=None, end=None):
    now_utc = normalize_to_utc(timezone.now())
    start_utc = normalize_to_utc(start) if start else now_utc
    end_utc = normalize_to_utc(end) if end else start_utc + timedelta(days=MAX_AVAILABILITY_WINDOW_DAYS)

    if end_utc <= start_utc:
        raise ValidationError("End datetime must be after start datetime.")
    if end_utc - start_utc > timedelta(days=MAX_AVAILABILITY_WINDOW_DAYS):
        raise ValidationError(f"Availability query window cannot exceed {MAX_AVAILABILITY_WINDOW_DAYS} days.")

    event_timezone = ZoneInfo(event.timezone)
    event_start_utc = datetime.combine(
        event.availability_start_date,
        time.min,
        tzinfo=event_timezone,
    ).astimezone(timezone.UTC)
    event_end_utc = datetime.combine(
        event.availability_end_date + timedelta(days=1),
        time.min,
        tzinfo=event_timezone,
    ).astimezone(timezone.UTC)

    clamped_start = max(start_utc, event_start_utc)
    clamped_end = min(end_utc, event_end_utc)
    if clamped_end <= clamped_start:
        return clamped_start, clamped_start

    return clamped_start, clamped_end
