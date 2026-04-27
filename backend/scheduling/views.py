from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event
from .serializers import (
    AvailabilityQuerySerializer,
    AvailabilityResponseSerializer,
    BookingInputSerializer,
    BookingOutputSerializer,
    EventDetailSerializer,
)
from .utils import SlotAlreadyBookedError, create_booking, generate_available_slots


def _validation_error_detail(exc):
    if hasattr(exc, "message_dict"):
        return exc.message_dict
    return exc.messages


def get_active_event(slug):
    return get_object_or_404(Event.objects.filter(is_active=True), slug=slug)


class EventDetailView(APIView):
    def get(self, request, slug):
        event = get_active_event(slug)
        return Response(EventDetailSerializer(event).data)


class EventAvailabilityView(APIView):
    def get(self, request, slug):
        event = get_active_event(slug)
        serializer = AvailabilityQuerySerializer(data=request.query_params, context={"event": event})
        serializer.is_valid(raise_exception=True)

        start = serializer.validated_data["start"]
        end = serializer.validated_data["end"]
        slots = generate_available_slots(event, start, end)

        response = AvailabilityResponseSerializer(
            {
                "event_timezone": str(event.timezone),
                "duration_minutes": event.duration_minutes,
                "slots": slots,
            }
        )
        return Response(response.data)


class EventBookingCreateView(APIView):
    def post(self, request, slug):
        event = get_active_event(slug)
        serializer = BookingInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            booking = create_booking(event, serializer.validated_data)
        except SlotAlreadyBookedError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except DjangoValidationError as exc:
            return Response(_validation_error_detail(exc), status=status.HTTP_400_BAD_REQUEST)

        return Response(BookingOutputSerializer(booking).data, status=status.HTTP_201_CREATED)
