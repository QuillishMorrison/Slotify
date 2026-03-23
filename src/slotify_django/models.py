from __future__ import annotations

from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _

from slotify_django.conf import get_default_timezone, get_event_choices


class Weekday(models.IntegerChoices):
    MONDAY = 0, _("Monday")
    TUESDAY = 1, _("Tuesday")
    WEDNESDAY = 2, _("Wednesday")
    THURSDAY = 3, _("Thursday")
    FRIDAY = 4, _("Friday")
    SATURDAY = 5, _("Saturday")
    SUNDAY = 6, _("Sunday")


class Schedule(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    timezone = models.CharField(max_length=64, default=get_default_timezone)
    slot_size_minutes = models.PositiveIntegerField(default=30)
    min_slot_size_minutes = models.PositiveIntegerField(default=15)
    allow_overbooking = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self) -> str:
        return self.name

    @property
    def slot_size(self) -> timedelta:
        return timedelta(minutes=self.slot_size_minutes)

    @property
    def min_slot_size(self) -> timedelta:
        return timedelta(minutes=self.min_slot_size_minutes)

    def active_events(self):
        return self.events.filter(is_cancelled=False).order_by("start")

    def active_rules(self):
        return self.availability_rules.filter(is_active=True).order_by("weekday", "start_time")


class AvailabilityRule(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="availability_rules")
    weekday = models.IntegerField(choices=Weekday.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    label = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["schedule", "weekday", "start_time", "end_time"]
        verbose_name = "Availability rule"
        verbose_name_plural = "Availability rules"

    def __str__(self) -> str:
        name = self.label or self.get_weekday_display()
        return f"{name}: {self.start_time} - {self.end_time}"


class ScheduleEvent(models.Model):
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=64, choices=get_event_choices)
    title = models.CharField(max_length=255, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    metadata = models.JSONField(default=dict, blank=True)
    tags = models.JSONField(default=list, blank=True)
    blocks_availability = models.BooleanField(default=True)
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["schedule", "start", "end", "id"]
        verbose_name = "Schedule event"
        verbose_name_plural = "Schedule events"

    def __str__(self) -> str:
        title = self.title or self.event_type
        return f"{title}: {self.start} - {self.end}"
