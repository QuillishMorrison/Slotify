from __future__ import annotations

from django.conf import settings


DEFAULT_EVENT_CHOICES = [
    ("work", "Work"),
    ("busy", "Busy"),
    ("lunch", "Lunch"),
    ("break", "Break"),
    ("block", "Block"),
]


def get_event_choices() -> list[tuple[str, str]]:
    return list(getattr(settings, "SLOTIFY_DJANGO_EVENT_CHOICES", DEFAULT_EVENT_CHOICES))


def get_default_timezone() -> str:
    return getattr(settings, "SLOTIFY_DJANGO_DEFAULT_TIMEZONE", "UTC")
