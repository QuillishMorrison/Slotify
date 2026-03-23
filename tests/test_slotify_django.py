from __future__ import annotations

from datetime import date, datetime, time
from zoneinfo import ZoneInfo

import django
import pytest
from django.conf import settings
from django.db import connection

if not settings.configured:
    settings.configure(
        SECRET_KEY="test-key",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "slotify_django",
        ],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        USE_TZ=True,
        TIME_ZONE="UTC",
    )
    django.setup()

from slotify_django.models import AvailabilityRule, Schedule, ScheduleEvent
from slotify_django.services import generate_slots


@pytest.fixture(scope="module", autouse=True)
def create_tables():
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Schedule)
        schema_editor.create_model(AvailabilityRule)
        schema_editor.create_model(ScheduleEvent)
    yield


def test_generate_slots_expands_rules_and_splits_busy_events():
    ScheduleEvent.objects.all().delete()
    AvailabilityRule.objects.all().delete()
    Schedule.objects.all().delete()

    schedule = Schedule.objects.create(
        name="Main schedule",
        slug="main-schedule",
        timezone="Europe/Moscow",
    )
    AvailabilityRule.objects.create(
        schedule=schedule,
        weekday=0,
        start_time=time(8, 0),
        end_time=time(23, 0),
        label="Daily window",
    )

    tz = ZoneInfo("Europe/Moscow")
    ScheduleEvent.objects.create(
        schedule=schedule,
        event_type="work",
        title="Work",
        start=datetime(2026, 3, 23, 10, 0, tzinfo=tz),
        end=datetime(2026, 3, 23, 12, 0, tzinfo=tz),
    )
    lunch = ScheduleEvent.objects.create(
        schedule=schedule,
        event_type="lunch",
        title="Lunch",
        start=datetime(2026, 3, 23, 14, 0, tzinfo=tz),
        end=datetime(2026, 3, 23, 15, 0, tzinfo=tz),
    )

    slots = generate_slots(schedule, start=date(2026, 3, 23), end=date(2026, 3, 23))

    assert [(slot.timerange.start.hour, slot.timerange.end.hour) for slot in slots] == [
        (5, 7),
        (9, 11),
        (12, 20),
    ]

    lunch.is_cancelled = True
    lunch.save(update_fields=["is_cancelled"])
    merged_slots = generate_slots(schedule, start=date(2026, 3, 23), end=date(2026, 3, 23))

    assert [(slot.timerange.start.hour, slot.timerange.end.hour) for slot in merged_slots] == [
        (5, 7),
        (9, 20),
    ]
