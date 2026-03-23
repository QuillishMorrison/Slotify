# slotify Guide

## Обзор

`slotify` строится вокруг трех идей:

1. события являются source of truth
2. слоты являются производным представлением
3. все политики оформляются как явные rules и strategies

## Core abstractions

- `TimeRange`: immutable интервал, нормализуемый в UTC
- `Event`: запись занятости или другого значимого события расписания
- `ScheduleDefinition`: границы расписания и безопасные дефолты
- `ScheduleState`: состояние расписания и версия для optimistic concurrency
- `Slot`: производный свободный интервал
- `Rule`: единица валидации
- `SlotGenerationStrategy`: стратегия генерации слотов

## Rules

Из коробки доступны:

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

- `DynamicFreeSlotStrategy` строит свободные интервалы как разницу между bounds и blocking events
- `FixedIntervalSlotStrategy` режет свободные окна на равные интервалы
- merge соседних совместимых free-slots выполняется отдельной helper-логикой

## Примеры API

Простой API:

```python
scheduler.book(...)
scheduler.cancel(...)
scheduler.get_slots(...)
scheduler.add_block(...)
```

Объектный API:

```python
scheduler.add_event(event, schedule_id="demo")
scheduler.add_rule(custom_rule)
scheduler.add_strategy(custom_strategy)
```

Декларативный API:

```python
scheduler.apply(BookCommand(...))
scheduler.evaluate(schedule_state)
```

## Расширяемость

- custom правила добавляются через `validate(schedule, event, context)`
- custom storage реализует `ScheduleRepository`
- custom slot generation реализует `SlotGenerationStrategy`
- recurrence вынесен в интерфейсы и roadmap, чтобы не усложнять v1

## Ограничения

- ядро гарантирует консистентность только в рамках процесса и корректной реализации repository
- для конкурентного доступа между процессами нужны транзакции и блокировки конкретного backend
- materialized slots пока не входят в core API хранения

## Roadmap

- v1: core engine, rules, in-memory storage, fixed/dynamic slots
- v2: recurrence expansion, SQLAlchemy/Django adapters, richer idempotency
- v3: materialized slot caches, advanced conflict resolution, ecosystem adapters
