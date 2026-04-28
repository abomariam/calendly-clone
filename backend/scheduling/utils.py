from datetime import datetime, time, timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

MAX_AVAILABILITY_WINDOW_DAYS = 31


def default_availability_start_date():
    return timezone.localdate()


def default_availability_end_date():
    return timezone.localdate() + timedelta(days=60)


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

    event_timezone = event.timezone
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


def generate_available_slots(event, start_utc, end_utc):
    start_utc = normalize_to_utc(start_utc)
    end_utc = normalize_to_utc(end_utc)
    if end_utc < start_utc:
        raise ValidationError("End datetime must be after start datetime.")
    if end_utc == start_utc:
        return []

    event_timezone = event.timezone
    duration = timedelta(minutes=event.duration_minutes)
    now_local = timezone.now().astimezone(event_timezone)
    local_start_date = start_utc.astimezone(event_timezone).date()
    local_end_date = end_utc.astimezone(event_timezone).date()
    rules_by_weekday = {rule.weekday: rule for rule in event.availability_rules.all()}
    booked_starts = set(
        event.bookings.filter(
            starts_at__gte=start_utc,
            starts_at__lt=end_utc,
        ).values_list("starts_at", flat=True)
    )

    slots = []
    local_date = local_start_date
    while local_date <= local_end_date:
        rule = rules_by_weekday.get(local_date.weekday())
        if rule and event.availability_start_date <= local_date <= event.availability_end_date:
            rule_start = datetime.combine(local_date, rule.start_time, tzinfo=event_timezone)
            rule_end = datetime.combine(local_date, rule.end_time, tzinfo=event_timezone)
            slot_start = rule_start
            while slot_start + duration <= rule_end:
                slot_end = slot_start + duration
                slot_start_utc = slot_start.astimezone(timezone.UTC)
                slot_end_utc = slot_end.astimezone(timezone.UTC)
                if (
                    now_local <= slot_start
                    and start_utc <= slot_start_utc
                    and slot_end_utc <= end_utc
                    and slot_start_utc not in booked_starts
                ):
                    slots.append({"starts_at": slot_start_utc, "ends_at": slot_end_utc})
                slot_start += duration
        local_date += timedelta(days=1)

    return slots


def is_bookable_slot(event, starts_at_utc):
    starts_at_utc = normalize_to_utc(starts_at_utc)
    if starts_at_utc < timezone.now():
        return False

    ends_at_utc = starts_at_utc + timedelta(minutes=event.duration_minutes)
    return any(
        slot["starts_at"] == starts_at_utc
        for slot in generate_available_slots(event, starts_at_utc, ends_at_utc)
    )


def create_booking(event, validated_payload):
    starts_at_utc = normalize_to_utc(validated_payload["starts_at"])

    if not is_bookable_slot(event, starts_at_utc):
        raise ValidationError({"starts_at": "Requested start time is not an available slot."})

    booking_data = {
        **validated_payload,
        "starts_at": starts_at_utc,
        "ends_at": starts_at_utc + timedelta(minutes=event.duration_minutes),
    }

    try:
        return event.bookings.create(**booking_data)
    except IntegrityError as exc:
        raise ValidationError({"starts_at": "Requested start time is not an available slot."}) from exc
