from datetime import timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.core.exceptions import ValidationError
from django.utils import timezone


def default_availability_start_date():
    return timezone.localdate()


def default_availability_end_date():
    return timezone.localdate() + timedelta(days=60)


def validate_timezone(value):
    try:
        ZoneInfo(value)
    except (ZoneInfoNotFoundError, TypeError, ValueError):
        raise ValidationError("%(value)s is not a valid IANA timezone.", params={"value": value})
