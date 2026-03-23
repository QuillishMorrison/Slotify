# slotify

Russian: see [README.md](README.md).

`slotify` is a production-oriented, headless Python scheduling engine for time ranges, slots, bookings, blocks, and scheduling rules.

## Positioning

This package is intended for developers embedding scheduling behavior into:

- web backends
- APIs and microservices
- internal tools
- CLI workflows
- reusable open-source libraries

It is framework-agnostic and storage-agnostic by design.

## Features

- timezone-aware API with UTC-normalized calculations
- source-of-truth event model plus derived slots
- pluggable rules and strategies
- optimistic concurrency hooks
- strong typing and modern Python packaging
- in-memory implementation for tests and prototyping

## Example

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
    metadata={"reason": "maintenance"},
)

available_slots = scheduler.get_slots("room-a")
```

## Docs

See the `docs/` directory for:

- overview
- quickstart
- concepts
- extensibility notes
- roadmap

