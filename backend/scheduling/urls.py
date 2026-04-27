from django.urls import path

from .views import EventAvailabilityView, EventBookingCreateView, EventDetailView

urlpatterns = [
    path("events/<slug:slug>/", EventDetailView.as_view(), name="event-detail"),
    path("events/<slug:slug>/availability/", EventAvailabilityView.as_view(), name="event-availability"),
    path("events/<slug:slug>/bookings/", EventBookingCreateView.as_view(), name="event-booking-create"),
]
