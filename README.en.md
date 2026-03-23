# slotify

Русская версия: [README.md](README.md).

`slotify` is a production-oriented scheduling engine with two layers:

- `slotify`: framework-agnostic core for time ranges, slots, bookings, blocks, and rules
- `slotify_django`: optional Django companion app with models, admin, and services

## Install

Core only:

```bash
python -m pip install slotify-engine
```

With Django support:

```bash
python -m pip install 'slotify-engine[django]'
```

For local development:

```bash
python -m pip install -e .[dev]
```

## Core example

```python
from datetime import UTC, datetime, timedelta

from slotify import InMemoryScheduleRepository, Scheduler
from slotify.domain import ScheduleDefinition, TimeRange

repository = InMemoryScheduleRepository()
scheduler = Scheduler(repository=repository)

repository.create_schedule(
    ScheduleDefinition(
        schedule_id="room-a",
        bounds=TimeRange(
            start=datetime(2026, 3, 23, 8, 0, tzinfo=UTC),
            end=datetime(2026, 3, 23, 18, 0, tzinfo=UTC),
        ),
        slot_size=timedelta(minutes=30),
        timezone="UTC",
    )
)

scheduler.add_block(
    "room-a",
    start=datetime(2026, 3, 23, 12, 0, tzinfo=UTC),
    end=datetime(2026, 3, 23, 13, 0, tzinfo=UTC),
)

available_slots = scheduler.get_slots("room-a")
```

## Django companion app

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...,
    "slotify_django",
]
```

Then run:

```bash
python manage.py migrate
```

You get reusable models out of the box:

- `slotify_django.Schedule`
- `slotify_django.AvailabilityRule`
- `slotify_django.ScheduleEvent`

And reusable services:

```python
from slotify_django.services import generate_slots

slots = generate_slots(schedule, start=date(2026, 3, 23), end=date(2026, 3, 30))
```

The admin also includes basic schedule and event management.

## Status

Version `0.1.0` is focused on a clean reusable core and a pragmatic Django starter layer. It does not implement distributed locking or full RRULE recurrence yet.
