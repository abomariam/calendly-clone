from datetime import date, time, timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from scheduling.models import Booking, Event, EventAvailabilityRule


class EventModelTests(TestCase):
    def test_default_dates_are_applied(self):
        event = Event(name="Intro Call", slug="intro-call")

        self.assertEqual(event.availability_start_date, timezone.localdate())
        self.assertEqual(event.availability_end_date, timezone.localdate() + timedelta(days=60))

    def test_rejects_invalid_timezone(self):
        with self.assertRaises(ValidationError) as context:
            Event(name="Intro Call", slug="intro-call", timezone="Not/AZone")

        self.assertEqual(
            context.exception.messages,
            ["Invalid timezone 'Not/AZone'"],
        )

    def test_rejects_invalid_date_range(self):
        event = Event(
            name="Intro Call",
            slug="intro-call",
            availability_start_date=date(2026, 5, 2),
            availability_end_date=date(2026, 5, 1),
        )

        with self.assertRaises(ValidationError) as context:
            event.full_clean()

        self.assertEqual(
            context.exception.message_dict["availability_end_date"],
            ["Availability end date must be on or after the start date."],
        )

    def test_rejects_non_positive_duration(self):
        event = Event(name="Intro Call", slug="intro-call", duration_minutes=0)

        with self.assertRaises(ValidationError) as context:
            event.full_clean()

        self.assertEqual(
            context.exception.message_dict["duration_minutes"],
            ["Ensure this value is greater than or equal to 1."],
        )


class EventAvailabilityRuleModelTests(TestCase):
    def make_event(self, **overrides):
        defaults = {
            "name": "Intro Call",
            "slug": "intro-call",
            "timezone": "Africa/Cairo",
        }
        defaults.update(overrides)
        return Event.objects.create(**defaults)

    def test_rejects_start_time_after_or_equal_to_end_time(self):
        event = self.make_event()
        rule = EventAvailabilityRule(
            event=event,
            weekday=EventAvailabilityRule.Weekday.MONDAY,
            start_time=time(10, 0),
            end_time=time(10, 0),
        )

        with self.assertRaises(ValidationError) as context:
            rule.full_clean()

        self.assertEqual(
            context.exception.message_dict["end_time"],
            ["End time must be after start time."],
        )

    def test_duplicate_weekday_rules_for_same_event_are_rejected(self):
        event = self.make_event()
        EventAvailabilityRule.objects.create(
            event=event,
            weekday=EventAvailabilityRule.Weekday.MONDAY,
            start_time=time(9, 0),
            end_time=time(10, 0),
        )

        with self.assertRaises(IntegrityError):
            EventAvailabilityRule.objects.create(
                event=event,
                weekday=EventAvailabilityRule.Weekday.MONDAY,
                start_time=time(10, 0),
                end_time=time(11, 0),
            )


class BookingModelTests(TestCase):
    def make_event(self, **overrides):
        defaults = {
            "name": "Intro Call",
            "slug": "intro-call",
            "timezone": "Africa/Cairo",
        }
        defaults.update(overrides)
        return Event.objects.create(**defaults)

    def test_duplicate_bookings_for_same_event_and_start_are_rejected(self):
        event = self.make_event()
        starts_at = timezone.datetime(2026, 5, 4, 7, 0, tzinfo=timezone.UTC)
        ends_at = starts_at + timedelta(minutes=event.duration_minutes)
        Booking.objects.create(
            event=event,
            invitee_name="Mona Hassan",
            invitee_email="mona@example.com",
            invitee_timezone="Europe/London",
            starts_at=starts_at,
            ends_at=ends_at,
        )

        with self.assertRaises(IntegrityError):
            Booking.objects.create(
                event=event,
                invitee_name="Ali Hassan",
                invitee_email="ali@example.com",
                invitee_timezone="Europe/London",
                starts_at=starts_at,
                ends_at=ends_at,
            )

    def test_rejects_invalid_invitee_timezone(self):
        event = self.make_event()
        starts_at = timezone.datetime(2026, 5, 4, 7, 0, tzinfo=timezone.UTC)
        with self.assertRaises(ValidationError) as context:
            Booking(
                event=event,
                invitee_name="Mona Hassan",
                invitee_email="mona@example.com",
                invitee_timezone="Not/AZone",
                starts_at=starts_at,
                ends_at=starts_at + timedelta(minutes=event.duration_minutes),
            )

        self.assertEqual(
            context.exception.messages,
            ["Invalid timezone 'Not/AZone'"],
        )
