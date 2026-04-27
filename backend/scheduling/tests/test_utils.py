from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from scheduling.models import Booking, Event, EventAvailabilityRule
from scheduling.utils import generate_available_slots, get_event_query_window, normalize_to_utc


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


class SlotGenerationTests(TestCase):
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

    def add_rule(self, event, weekday=EventAvailabilityRule.Weekday.MONDAY, start=time(9, 0), end=time(11, 0)):
        return EventAvailabilityRule.objects.create(
            event=event,
            weekday=weekday,
            start_time=start,
            end_time=end,
        )

    def test_generates_four_30_minute_slots_for_two_hour_rule(self):
        event = self.make_event(duration_minutes=30)
        self.add_rule(event)

        slots = generate_available_slots(
            event,
            start_utc=datetime(2026, 5, 4, 0, 0, tzinfo=timezone.UTC),
            end_utc=datetime(2026, 5, 5, 0, 0, tzinfo=timezone.UTC),
        )

        self.assertEqual(
            slots,
            [
                {
                    "starts_at": datetime(2026, 5, 4, 6, 0, tzinfo=timezone.UTC),
                    "ends_at": datetime(2026, 5, 4, 6, 30, tzinfo=timezone.UTC),
                },
                {
                    "starts_at": datetime(2026, 5, 4, 6, 30, tzinfo=timezone.UTC),
                    "ends_at": datetime(2026, 5, 4, 7, 0, tzinfo=timezone.UTC),
                },
                {
                    "starts_at": datetime(2026, 5, 4, 7, 0, tzinfo=timezone.UTC),
                    "ends_at": datetime(2026, 5, 4, 7, 30, tzinfo=timezone.UTC),
                },
                {
                    "starts_at": datetime(2026, 5, 4, 7, 30, tzinfo=timezone.UTC),
                    "ends_at": datetime(2026, 5, 4, 8, 0, tzinfo=timezone.UTC),
                },
            ],
        )

    def test_generates_two_45_minute_slots_for_two_hour_rule(self):
        event = self.make_event(duration_minutes=45)
        self.add_rule(event)

        slots = generate_available_slots(
            event,
            start_utc=datetime(2026, 5, 4, 0, 0, tzinfo=timezone.UTC),
            end_utc=datetime(2026, 5, 5, 0, 0, tzinfo=timezone.UTC),
        )

        self.assertEqual(
            [slot["starts_at"] for slot in slots],
            [
                datetime(2026, 5, 4, 6, 0, tzinfo=timezone.UTC),
                datetime(2026, 5, 4, 6, 45, tzinfo=timezone.UTC),
            ],
        )

    def test_excludes_booked_slots(self):
        event = self.make_event(duration_minutes=30)
        self.add_rule(event)
        booked_start = datetime(2026, 5, 4, 6, 30, tzinfo=timezone.UTC)
        Booking.objects.create(
            event=event,
            invitee_name="Mona Hassan",
            invitee_email="mona@example.com",
            invitee_timezone="Europe/London",
            starts_at=booked_start,
            ends_at=booked_start + timedelta(minutes=30),
        )

        slots = generate_available_slots(
            event,
            start_utc=datetime(2026, 5, 4, 0, 0, tzinfo=timezone.UTC),
            end_utc=datetime(2026, 5, 5, 0, 0, tzinfo=timezone.UTC),
        )

        self.assertNotIn(booked_start, [slot["starts_at"] for slot in slots])
        self.assertEqual(len(slots), 3)

    def test_excludes_slots_outside_event_date_range(self):
        event = self.make_event(
            duration_minutes=30,
            availability_start_date=date(2026, 5, 5),
            availability_end_date=date(2026, 5, 5),
        )
        self.add_rule(event, weekday=EventAvailabilityRule.Weekday.MONDAY)
        self.add_rule(event, weekday=EventAvailabilityRule.Weekday.TUESDAY)

        slots = generate_available_slots(
            event,
            start_utc=datetime(2026, 5, 4, 0, 0, tzinfo=timezone.UTC),
            end_utc=datetime(2026, 5, 6, 0, 0, tzinfo=timezone.UTC),
        )

        self.assertEqual(
            [slot["starts_at"] for slot in slots],
            [
                datetime(2026, 5, 5, 6, 0, tzinfo=timezone.UTC),
                datetime(2026, 5, 5, 6, 30, tzinfo=timezone.UTC),
                datetime(2026, 5, 5, 7, 0, tzinfo=timezone.UTC),
                datetime(2026, 5, 5, 7, 30, tzinfo=timezone.UTC),
            ],
        )

    def test_24_7_availability_generates_slots_without_storing_slot_rows(self):
        event = self.make_event(duration_minutes=60)
        for weekday in EventAvailabilityRule.Weekday.values:
            self.add_rule(event, weekday=weekday, start=time(0, 0), end=time(23, 59))

        slots = generate_available_slots(
            event,
            start_utc=datetime(2026, 5, 4, 0, 0, tzinfo=timezone.UTC),
            end_utc=datetime(2026, 5, 5, 0, 0, tzinfo=timezone.UTC),
        )

        self.assertEqual(len(slots), 23)
        self.assertEqual(EventAvailabilityRule.objects.filter(event=event).count(), 7)
        self.assertEqual(Booking.objects.filter(event=event).count(), 0)
