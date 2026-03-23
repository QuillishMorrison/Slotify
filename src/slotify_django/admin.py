from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from slotify_django.models import AvailabilityRule, Schedule, ScheduleEvent
from slotify_django.services import generate_slots


class AvailabilityRuleInline(admin.TabularInline):
    model = AvailabilityRule
    extra = 1


@admin.action(description="Cancel selected events")
def cancel_events(modeladmin, request, queryset):
    updated = queryset.update(is_cancelled=True)
    modeladmin.message_user(request, _("Cancelled %(count)s events") % {"count": updated}, level=messages.SUCCESS)


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "timezone", "slot_size_minutes", "is_active", "updated_at")
    list_filter = ("is_active", "timezone")
    search_fields = ("name", "slug")
    inlines = [AvailabilityRuleInline]
    readonly_fields = ("created_at", "updated_at")


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = ("schedule", "weekday", "start_time", "end_time", "label", "is_active")
    list_filter = ("weekday", "is_active")
    search_fields = ("schedule__name", "label")


@admin.register(ScheduleEvent)
class ScheduleEventAdmin(admin.ModelAdmin):
    list_display = ("title", "schedule", "event_type", "start", "end", "blocks_availability", "is_cancelled")
    list_filter = ("event_type", "blocks_availability", "is_cancelled", "schedule")
    search_fields = ("title", "schedule__name")
    actions = [cancel_events]
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        slots = generate_slots(obj.schedule, obj.start.date(), obj.start.date())
        self.message_user(request, _("Schedule rebuilt virtually. %(count)s free slots available for that day.") % {"count": len(slots)}, level=messages.INFO)
