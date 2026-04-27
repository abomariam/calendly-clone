from datetime import date, datetime, timedelta

from django.test import TestCase
from django.utils import timezone
from freezegun import freeze_time

from scheduling.models import Booking, Event
from scheduling.serializers import (
    AvailabilityQuerySerializer,
    AvailabilityResponseSerializer,
    BookingInputSerializer,
    BookingOutputSerializer,
    EventDetailSerializer,
)


class EventDetailSerializerTests(TestCase):
    def test_serializes_public_event_fields(self):
        event = Event.objects.create(
            name="Intro Call",
            slug="intro-call-a8f3k2",
            description="We will discuss the project scope.",
            duration_minutes=30,
            timezone="Africa/Cairo",
            availability_start_date=date(2026, 5, 1),
            availability_end_date=date(2026, 6, 1),
        )

        self.assertEqual(
            EventDetailSerializer(event).data,
            {
                "slug": "intro-call-a8f3k2",
                "name": "Intro Call",
                "description": "We will discuss the project scope.",
                "duration_minutes": 30,
                "timezone": "Africa/Cairo",
                "availability_start_date": "2026-05-01",
                "availability_end_date": "2026-06-01",
            },
        )


class AvailabilityQuerySerializerTests(TestCase):
    def make_event(self):
        return Event.objects.create(
            name="Intro Call",
            slug="intro-call",
            timezone="Africa/Cairo",
            availability_start_date=date(2026, 5, 1),
            availability_end_date=date(2026, 6, 30),
        )

    def test_validates_and_normalizes_query_datetimes_to_utc(self):
        serializer = AvailabilityQuerySerializer(
            data={
                "start": "2026-05-04T09:00:00+02:00",
                "end": "2026-05-04T10:00:00+02:00",
            },
            context={"event": self.make_event()},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["start"], datetime(2026, 5, 4, 7, 0, tzinfo=timezone.UTC))
        self.assertEqual(serializer.validated_data["end"], datetime(2026, 5, 4, 8, 0, tzinfo=timezone.UTC))

    @freeze_time("2026-05-04T07:00:00Z")
    def test_defaults_query_window_when_dates_are_omitted(self):
        serializer = AvailabilityQuerySerializer(data={}, context={"event": self.make_event()})

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["start"], datetime(2026, 5, 4, 7, 0, tzinfo=timezone.UTC))
        self.assertEqual(serializer.validated_data["end"], datetime(2026, 6, 4, 7, 0, tzinfo=timezone.UTC))

    def test_treats_naive_query_datetime_as_utc(self):
        serializer = AvailabilityQuerySerializer(
            data={
                "start": "2026-05-04T09:00:00",
                "end": "2026-05-04T10:00:00",
            },
            context={"event": self.make_event()},
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["start"], datetime(2026, 5, 4, 9, 0, tzinfo=timezone.UTC))
        self.assertEqual(serializer.validated_data["end"], datetime(2026, 5, 4, 10, 0, tzinfo=timezone.UTC))

    def test_rejects_oversized_query_window(self):
        serializer = AvailabilityQuerySerializer(
            data={
                "start": "2026-05-01T00:00:00Z",
                "end": "2026-06-02T00:00:00Z",
            },
            context={"event": self.make_event()},
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["non_field_errors"], ["Availability query window cannot exceed 31 days."])


class AvailabilityResponseSerializerTests(TestCase):
    def test_serializes_utc_slots(self):
        serializer = AvailabilityResponseSerializer(
            {
                "event_timezone": "Africa/Cairo",
                "duration_minutes": 30,
                "slots": [
                    {
                        "starts_at": datetime(2026, 5, 4, 7, 0, tzinfo=timezone.UTC),
                        "ends_at": datetime(2026, 5, 4, 7, 30, tzinfo=timezone.UTC),
                    }
                ],
            }
        )

        self.assertEqual(
            serializer.data,
            {
                "event_timezone": "Africa/Cairo",
                "duration_minutes": 30,
                "slots": [
                    {
                        "starts_at": "2026-05-04T07:00:00Z",
                        "ends_at": "2026-05-04T07:30:00Z",
                    }
                ],
            },
        )


class BookingInputSerializerTests(TestCase):
    def test_validates_and_normalizes_booking_input(self):
        serializer = BookingInputSerializer(
            data={
                "invitee_name": "Mona Hassan",
                "invitee_email": "mona@example.com",
                "note": "I want to discuss pricing.",
                "invitee_timezone": "Europe/London",
                "starts_at": "2026-05-04T09:00:00+02:00",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["starts_at"], datetime(2026, 5, 4, 7, 0, tzinfo=timezone.UTC))

    def test_rejects_invalid_email(self):
        serializer = BookingInputSerializer(
            data={
                "invitee_name": "Mona Hassan",
                "invitee_email": "not-an-email",
                "invitee_timezone": "Europe/London",
                "starts_at": "2026-05-04T07:00:00Z",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("invitee_email", serializer.errors)

    def test_rejects_invalid_timezone(self):
        serializer = BookingInputSerializer(
            data={
                "invitee_name": "Mona Hassan",
                "invitee_email": "mona@example.com",
                "invitee_timezone": "Not/AZone",
                "starts_at": "2026-05-04T07:00:00Z",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["invitee_timezone"], ["A valid timezone is required."])

    def test_treats_naive_starts_at_as_utc(self):
        serializer = BookingInputSerializer(
            data={
                "invitee_name": "Mona Hassan",
                "invitee_email": "mona@example.com",
                "invitee_timezone": "Europe/London",
                "starts_at": "2026-05-04T07:00:00",
            }
        )

        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.validated_data["starts_at"], datetime(2026, 5, 4, 7, 0, tzinfo=timezone.UTC))

    def test_requires_invitee_fields_and_starts_at(self):
        serializer = BookingInputSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors["invitee_name"], ["This field is required."])
        self.assertEqual(serializer.errors["invitee_email"], ["This field is required."])
        self.assertEqual(serializer.errors["invitee_timezone"], ["This field is required."])
        self.assertEqual(serializer.errors["starts_at"], ["This field is required."])


class BookingOutputSerializerTests(TestCase):
    def test_serializes_booking_response(self):
        event = Event.objects.create(name="Intro Call", slug="intro-call-a8f3k2", timezone="Africa/Cairo")
        starts_at = datetime(2026, 5, 4, 7, 0, tzinfo=timezone.UTC)
        booking = Booking.objects.create(
            event=event,
            invitee_name="Mona Hassan",
            invitee_email="mona@example.com",
            note="I want to discuss pricing.",
            invitee_timezone="Europe/London",
            starts_at=starts_at,
            ends_at=starts_at + timedelta(minutes=30),
        )

        self.assertEqual(
            BookingOutputSerializer(booking).data,
            {
                "id": booking.id,
                "event": "intro-call-a8f3k2",
                "invitee_name": "Mona Hassan",
                "invitee_email": "mona@example.com",
                "note": "I want to discuss pricing.",
                "invitee_timezone": "Europe/London",
                "starts_at": "2026-05-04T07:00:00Z",
                "ends_at": "2026-05-04T07:30:00Z",
            },
        )
