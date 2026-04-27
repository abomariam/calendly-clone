from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from timezone_field.rest_framework import TimeZoneSerializerField

from .models import Booking, Event
from .utils import get_event_query_window


class EventDetailSerializer(serializers.ModelSerializer):
    timezone = TimeZoneSerializerField(read_only=True)

    class Meta:
        model = Event
        fields = [
            "slug",
            "name",
            "description",
            "duration_minutes",
            "timezone",
            "availability_start_date",
            "availability_end_date",
        ]


class AvailabilityQuerySerializer(serializers.Serializer):
    start = serializers.DateTimeField(required=False, default_timezone=None)
    end = serializers.DateTimeField(required=False, default_timezone=None)

    def validate(self, attrs):
        event = self.context.get("event")
        if not event:
            return attrs

        try:
            start, end = get_event_query_window(event, attrs.get("start"), attrs.get("end"))
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.messages) from exc

        attrs["start"] = start
        attrs["end"] = end
        return attrs


class AvailabilitySlotSerializer(serializers.Serializer):
    starts_at = serializers.DateTimeField(default_timezone=None)
    ends_at = serializers.DateTimeField(default_timezone=None)


class AvailabilityResponseSerializer(serializers.Serializer):
    event_timezone = serializers.CharField()
    duration_minutes = serializers.IntegerField()
    slots = AvailabilitySlotSerializer(many=True)


class BookingInputSerializer(serializers.Serializer):
    invitee_name = serializers.CharField(max_length=255)
    invitee_email = serializers.EmailField()
    note = serializers.CharField(required=False, allow_blank=True)
    invitee_timezone = TimeZoneSerializerField()
    starts_at = serializers.DateTimeField(default_timezone=None)


class BookingOutputSerializer(serializers.ModelSerializer):
    event = serializers.SlugRelatedField(read_only=True, slug_field="slug")
    invitee_timezone = TimeZoneSerializerField(read_only=True)
    starts_at = serializers.DateTimeField(default_timezone=None)
    ends_at = serializers.DateTimeField(default_timezone=None)

    class Meta:
        model = Booking
        fields = [
            "id",
            "event",
            "invitee_name",
            "invitee_email",
            "note",
            "invitee_timezone",
            "starts_at",
            "ends_at",
        ]
