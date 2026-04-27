from datetime import date, datetime, timedelta

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from .utils import default_availability_end_date, default_availability_start_date, validate_timezone


class Event(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=30, validators=[MinValueValidator(1)])
    availability_start_date = models.DateField(default=default_availability_start_date)
    availability_end_date = models.DateField(default=default_availability_end_date)
    timezone = models.CharField(max_length=64, default="UTC", validators=[validate_timezone])
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        if self.availability_end_date < self.availability_start_date:
            raise ValidationError(
                {"availability_end_date": "Availability end date must be on or after the start date."}
            )

    def __str__(self):
        return self.name


class EventAvailabilityRule(models.Model):
    class Weekday(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="availability_rules")
    weekday = models.PositiveSmallIntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["event", "weekday"], name="unique_event_weekday_availability"),
        ]
        ordering = ["event", "weekday", "start_time"]

    def clean(self):
        super().clean()
        if self.start_time >= self.end_time:
            raise ValidationError({"end_time": "End time must be after start time."})
        if self.event_id:
            window_start = datetime.combine(date.min, self.start_time)
            window_end = datetime.combine(date.min, self.end_time)
            window_duration = window_end - window_start
            slot_duration = timedelta(minutes=self.event.duration_minutes)
            if window_duration < slot_duration:
                raise ValidationError({"end_time": "Availability window must fit at least one slot."})

    def __str__(self):
        return f"{self.event} {self.get_weekday_display()} {self.start_time}-{self.end_time}"


class Booking(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="bookings")
    invitee_name = models.CharField(max_length=255)
    invitee_email = models.EmailField()
    note = models.TextField(blank=True)
    invitee_timezone = models.CharField(max_length=64, validators=[validate_timezone])
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["event", "starts_at"], name="unique_event_booking_start"),
        ]
        ordering = ["-starts_at"]

    def clean(self):
        super().clean()
        if self.starts_at and timezone.is_naive(self.starts_at):
            raise ValidationError({"starts_at": "Start datetime must be timezone-aware."})
        if self.ends_at and timezone.is_naive(self.ends_at):
            raise ValidationError({"ends_at": "End datetime must be timezone-aware."})
        if self.starts_at and self.ends_at and self.ends_at <= self.starts_at:
            raise ValidationError({"ends_at": "End datetime must be after start datetime."})
        if self.event_id and self.starts_at and self.ends_at:
            expected_ends_at = self.starts_at + timedelta(minutes=self.event.duration_minutes)
            if self.ends_at != expected_ends_at:
                raise ValidationError({"ends_at": "End datetime must match the event duration."})

    def save(self, *args, **kwargs):
        if self.event_id and self.starts_at and not self.ends_at:
            self.ends_at = self.starts_at + timedelta(minutes=self.event.duration_minutes)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.invitee_name} - {self.event} at {self.starts_at}"
