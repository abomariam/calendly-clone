from datetime import date, datetime, time, timedelta

from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from scheduling.models import Booking, Event, EventAvailabilityRule


class PublicEventApiTests(APITestCase):
    def make_event(self, **overrides):
        defaults = {
            "name": "Intro Call",
            "slug": "intro-call",
            "description": "We will discuss the project scope.",
            "duration_minutes": 30,
            "timezone": "Africa/Cairo",
            "availability_start_date": date(2026, 5, 1),
            "availability_end_date": date(2026, 5, 31),
            "is_active": True,
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

    def booking_payload(self, starts_at="2026-05-04T06:00:00Z", **overrides):
        payload = {
            "invitee_name": "Mona Hassan",
            "invitee_email": "mona@example.com",
            "note": "I want to discuss pricing.",
            "invitee_timezone": "Europe/London",
            "starts_at": starts_at,
        }
        payload.update(overrides)
        return payload

    def assert_event_is_hidden(self, slug):
        endpoints = [
            ("event-detail", "get", None),
            ("event-availability", "get", None),
            ("event-booking-create", "post", self.booking_payload()),
        ]

        for url_name, method, data in endpoints:
            response = getattr(self.client, method)(reverse(url_name, kwargs={"slug": slug}), data=data)
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_event_detail_returns_active_event_metadata(self):
        event = self.make_event(slug="intro-call-a8f3k2")

        response = self.client.get(reverse("event-detail", kwargs={"slug": event.slug}))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "slug": "intro-call-a8f3k2",
                "name": "Intro Call",
                "description": "We will discuss the project scope.",
                "duration_minutes": 30,
                "timezone": "Africa/Cairo",
                "availability_start_date": "2026-05-01",
                "availability_end_date": "2026-05-31",
            },
        )

    def test_inactive_events_are_hidden_from_public_endpoints(self):
        event = self.make_event(is_active=False)

        self.assert_event_is_hidden(event.slug)

    def test_missing_events_return_404_from_public_endpoints(self):
        self.assert_event_is_hidden("missing-event")

    def test_availability_returns_utc_slots_without_storing_generated_slots(self):
        event = self.make_event()
        self.add_rule(event)

        response = self.client.get(
            reverse("event-availability", kwargs={"slug": event.slug}),
            {
                "start": "2026-05-04T00:00:00Z",
                "end": "2026-05-05T00:00:00Z",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "event_timezone": "Africa/Cairo",
                "duration_minutes": 30,
                "slots": [
                    {"starts_at": "2026-05-04T06:00:00Z", "ends_at": "2026-05-04T06:30:00Z"},
                    {"starts_at": "2026-05-04T06:30:00Z", "ends_at": "2026-05-04T07:00:00Z"},
                    {"starts_at": "2026-05-04T07:00:00Z", "ends_at": "2026-05-04T07:30:00Z"},
                    {"starts_at": "2026-05-04T07:30:00Z", "ends_at": "2026-05-04T08:00:00Z"},
                ],
            },
        )
        self.assertEqual(EventAvailabilityRule.objects.filter(event=event).count(), 1)
        self.assertEqual(Booking.objects.filter(event=event).count(), 0)

    def test_availability_rejects_oversized_windows(self):
        event = self.make_event()

        response = self.client.get(
            reverse("event-availability", kwargs={"slug": event.slug}),
            {
                "start": "2026-05-01T00:00:00Z",
                "end": "2026-06-02T00:00:00Z",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"non_field_errors": ["Availability query window cannot exceed 31 days."]})

    @freeze_time("2026-05-01T00:00:00Z")
    def test_booking_creates_booking(self):
        event = self.make_event()
        self.add_rule(event)

        response = self.client.post(
            reverse("event-booking-create", kwargs={"slug": event.slug}),
            data=self.booking_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        booking = Booking.objects.get()
        self.assertEqual(booking.event, event)
        self.assertEqual(booking.invitee_email, "mona@example.com")
        self.assertEqual(booking.starts_at, datetime(2026, 5, 4, 6, 0, tzinfo=timezone.UTC))
        self.assertEqual(booking.ends_at, datetime(2026, 5, 4, 6, 30, tzinfo=timezone.UTC))
        self.assertEqual(
            response.json(),
            {
                "id": booking.id,
                "event": "intro-call",
                "invitee_name": "Mona Hassan",
                "invitee_email": "mona@example.com",
                "note": "I want to discuss pricing.",
                "invitee_timezone": "Europe/London",
                "starts_at": "2026-05-04T06:00:00Z",
                "ends_at": "2026-05-04T06:30:00Z",
            },
        )

    @freeze_time("2026-05-01T00:00:00Z")
    def test_booking_rejects_invalid_email(self):
        event = self.make_event()
        self.add_rule(event)

        response = self.client.post(
            reverse("event-booking-create", kwargs={"slug": event.slug}),
            data=self.booking_payload(invitee_email="not-an-email"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invitee_email", response.json())
        self.assertEqual(Booking.objects.count(), 0)

    @freeze_time("2026-05-01T00:00:00Z")
    def test_booking_rejects_invalid_timezone(self):
        event = self.make_event()
        self.add_rule(event)

        response = self.client.post(
            reverse("event-booking-create", kwargs={"slug": event.slug}),
            data=self.booking_payload(invitee_timezone="Not/AZone"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["invitee_timezone"], ["A valid timezone is required."])
        self.assertEqual(Booking.objects.count(), 0)

    @freeze_time("2026-05-01T00:00:00Z")
    def test_booking_rejects_non_slot_start(self):
        event = self.make_event()
        self.add_rule(event)

        response = self.client.post(
            reverse("event-booking-create", kwargs={"slug": event.slug}),
            data=self.booking_payload(starts_at="2026-05-04T06:15:00Z"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"starts_at": ["Requested start time is not an available slot."]})
        self.assertEqual(Booking.objects.count(), 0)

    @freeze_time("2026-05-01T00:00:00Z")
    def test_booking_rejects_duplicate_slot_with_400(self):
        event = self.make_event()
        self.add_rule(event)
        starts_at = datetime(2026, 5, 4, 6, 0, tzinfo=timezone.UTC)
        Booking.objects.create(
            event=event,
            invitee_name="Mona Hassan",
            invitee_email="mona@example.com",
            invitee_timezone="Europe/London",
            starts_at=starts_at,
            ends_at=starts_at + timedelta(minutes=event.duration_minutes),
        )

        response = self.client.post(
            reverse("event-booking-create", kwargs={"slug": event.slug}),
            data=self.booking_payload(),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json(), {"starts_at": ["Requested start time is not an available slot."]})
        self.assertEqual(Booking.objects.count(), 1)
