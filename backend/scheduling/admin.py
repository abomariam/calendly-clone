import secrets

from django.contrib import admin
from django.utils.text import slugify

from .models import Booking, Event, EventAvailabilityRule


def generate_unique_event_slug(name):
    base_slug = slugify(name) or "event"
    base_slug = base_slug[:248].strip("-") or "event"

    while True:
        suffix = secrets.token_hex(3)
        slug = f"{base_slug}-{suffix}"
        if not Event.objects.filter(slug=slug).exists():
            return slug


class EventAvailabilityRuleInline(admin.TabularInline):
    model = EventAvailabilityRule
    extra = 7
    max_num = 7


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    inlines = [EventAvailabilityRuleInline]
    list_display = (
        "name",
        "slug",
        "duration_minutes",
        "timezone",
        "availability_start_date",
        "availability_end_date",
        "is_active",
    )
    list_filter = ("is_active", "timezone")
    readonly_fields = ("slug",)
    search_fields = ("name", "slug", "description")

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = generate_unique_event_slug(obj.name)
        super().save_model(request, obj, form, change)


@admin.register(EventAvailabilityRule)
class EventAvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = ("event", "weekday", "start_time", "end_time")
    list_filter = ("weekday",)
    search_fields = ("event__name", "event__slug")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("event", "invitee_name", "invitee_email", "starts_at", "ends_at", "created_at")
    list_filter = ("event", "invitee_timezone")
    search_fields = ("event__name", "event__slug", "invitee_name", "invitee_email")
