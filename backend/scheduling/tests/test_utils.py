from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from scheduling.models import Event
from scheduling.utils import get_event_query_window, normalize_to_utc


class SchedulingUtilityTests(TestCase):
    def make_event(self, **overrides):
        defaults = {
            "name": "Intro Call",
            "slug": "intro-call",
            "timezone": "Africa/Cairo",
            "availability_start_date": date(2026, 5, 1),
            "availability_end_date": date(2026, 5, 31),
        }
        defaults.update(overrides)
        return Event.objects.create(**defaults)

    def test_normalize_to_utc_converts_aware_datetime(self):
        value = datetime(2026, 5, 4, 10, 0, tzinfo=ZoneInfo("Africa/Cairo"))

        self.assertEqual(
            normalize_to_utc(value),
            datetime(2026, 5, 4, 7, 0, tzinfo=timezone.UTC),
        )

    def test_normalize_to_utc_rejects_naive_datetime(self):
        with self.assertRaises(ValidationError) as context:
            normalize_to_utc(datetime(2026, 5, 4, 10, 0))

        self.assertEqual(context.exception.messages, ["Datetime must be timezone-aware."])

    @freeze_time("2026-05-04T07:00:00Z")
    def test_query_window_defaults_to_near_term_window(self):
        event = self.make_event(availability_end_date=date(2026, 6, 30))
        now = datetime(2026, 5, 4, 7, 0, tzinfo=timezone.UTC)

        start_utc, end_utc = get_event_query_window(event)

        self.assertEqual(start_utc, now)
        self.assertEqual(end_utc, now + timedelta(days=31))

    def test_query_window_rejects_reversed_window(self):
        event = self.make_event()

        with self.assertRaises(ValidationError) as context:
            get_event_query_window(
                event,
                start=datetime(2026, 5, 5, 0, 0, tzinfo=timezone.UTC),
                end=datetime(2026, 5, 4, 0, 0, tzinfo=timezone.UTC),
            )

        self.assertEqual(context.exception.messages, ["End datetime must be after start datetime."])

    def test_query_window_rejects_windows_longer_than_31_days(self):
        event = self.make_event()

        with self.assertRaises(ValidationError) as context:
            get_event_query_window(
                event,
                start=datetime(2026, 5, 1, 0, 0, tzinfo=timezone.UTC),
                end=datetime(2026, 6, 2, 0, 0, tzinfo=timezone.UTC),
            )

        self.assertEqual(context.exception.messages, ["Availability query window cannot exceed 31 days."])

    def test_query_window_clamps_to_event_date_range(self):
        event = self.make_event()

        start_utc, end_utc = get_event_query_window(
            event,
            start=datetime(2026, 4, 30, 0, 0, tzinfo=timezone.UTC),
            end=datetime(2026, 5, 2, 0, 0, tzinfo=timezone.UTC),
        )

        self.assertEqual(start_utc, datetime(2026, 4, 30, 21, 0, tzinfo=timezone.UTC))
        self.assertEqual(end_utc, datetime(2026, 5, 2, 0, 0, tzinfo=timezone.UTC))

    def test_query_window_returns_empty_window_when_outside_event_date_range(self):
        event = self.make_event()

        start_utc, end_utc = get_event_query_window(
            event,
            start=datetime(2026, 4, 1, 0, 0, tzinfo=timezone.UTC),
            end=datetime(2026, 4, 2, 0, 0, tzinfo=timezone.UTC),
        )

        self.assertEqual(start_utc, datetime(2026, 4, 30, 21, 0, tzinfo=timezone.UTC))
        self.assertEqual(end_utc, start_utc)
