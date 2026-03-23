# slotify Guide

## Overview

`slotify` is built around three ideas:

1. events are the source of truth
2. slots are derived representations
3. policies live in explicit rules and strategies

## Core abstractions

- `TimeRange`: immutable interval normalized to UTC
- `Event`: occupancy or scheduling record
- `ScheduleDefinition`: bounds and safe defaults
- `ScheduleState`: current state plus optimistic concurrency version
- `Slot`: derived free interval
- `Rule`: validation unit
- `SlotGenerationStrategy`: slot derivation strategy

## Rules

Built-in rules include:

- `StartBeforeEndRule`
- `WithinBoundsRule`
- `NoOverlapRule`
- `MinDurationRule`
- `MaxDurationRule`
- `NoPastBookingRule`
- `LeadTimeRule`
- `BufferBetweenBookingsRule`
- `EventIdUniquenessRule`

## Slot generation

- `DynamicFreeSlotStrategy` subtracts blocking events from bounds
- `FixedIntervalSlotStrategy` slices free windows into regular intervals
- adjacent free-slot merge is implemented as helper logic

## API examples

Simple API:

```python
scheduler.book(...)
scheduler.cancel(...)
scheduler.get_slots(...)
scheduler.add_block(...)
```

Object API:

```python
scheduler.add_event(event, schedule_id="demo")
scheduler.add_rule(custom_rule)
scheduler.add_strategy(custom_strategy)
```

Declarative API:

```python
scheduler.apply(BookCommand(...))
scheduler.evaluate(schedule_state)
```

## Extensibility

- implement `validate(schedule, event, context)` for custom rules
- implement `ScheduleRepository` for custom storage
- implement `SlotGenerationStrategy` for custom slot logic
- recurrence is intentionally interface-first in v1

## Limitations

- core guarantees consistency only inside one process plus a correct repository implementation
- cross-process safety must be enforced by the storage/backend layer
- materialized slot persistence is outside the v1 core

## Roadmap

- v1: core engine, rules, in-memory storage, fixed/dynamic slots
- v2: recurrence expansion, SQLAlchemy/Django adapters, richer idempotency
- v3: materialized slot caches, advanced conflict resolution, ecosystem adapters
