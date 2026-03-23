from __future__ import annotations

from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from slotify import InMemoryScheduleRepository, Scheduler
from slotify.domain import Event, ScheduleDefinition, TimeRange
from slotify.exceptions import ConflictError, ConcurrencyError, ValidationError
from slotify.rules import BufferBetweenBookingsRule, LeadTimeRule
from slotify.strategies import FixedIntervalSlotStrategy


@pytest.fixture()
def repository() -> InMemoryScheduleRepository:
    return InMemoryScheduleRepository()


@pytest.fixture()
def schedule_definition() -> ScheduleDefinition:
    return ScheduleDefinition(
        schedule_id="demo",
        bounds=TimeRange(
            start=datetime(2026, 3, 23, 9, 0, tzinfo=UTC),
            end=datetime(2026, 3, 23, 17, 0, tzinfo=UTC),
        ),
        timezone="Europe/Moscow",
        slot_size=timedelta(minutes=30),
        min_slot_size=timedelta(minutes=15),
    )


@pytest.fixture()
def scheduler(repository: InMemoryScheduleRepository, schedule_definition: ScheduleDefinition) -> Scheduler:
    repository.create_schedule(schedule_definition)
    return Scheduler(repository=repository)


def test_timerange_normalizes_to_utc() -> None:
    local = ZoneInfo("Europe/Moscow")
    interval = TimeRange(
        start=datetime(2026, 3, 23, 12, 0, tzinfo=local),
        end=datetime(2026, 3, 23, 13, 0, tzinfo=local),
    )

    assert interval.start.tzinfo == UTC
    assert interval.start.hour == 9
    assert interval.end.hour == 10


def test_book_splits_dynamic_free_slots(scheduler: Scheduler) -> None:
    scheduler.book(
        "demo",
        start=datetime(2026, 3, 23, 10, 0, tzinfo=UTC),
        end=datetime(2026, 3, 23, 11, 0, tzinfo=UTC),
    )

    slots = scheduler.get_slots("demo")

    assert [(slot.timerange.start.hour, slot.timerange.end.hour) for slot in slots] == [(9, 10), (11, 17)]


def test_cancel_restores_merged_free_slot(scheduler: Scheduler) -> None:
    booking = scheduler.book(
        "demo",
        start=datetime(2026, 3, 23, 10, 0, tzinfo=UTC),
        end=datetime(2026, 3, 23, 11, 0, tzinfo=UTC),
    )

    scheduler.cancel("demo", booking.event_id)
    slots = scheduler.get_slots("demo")

    assert len(slots) == 1
    assert slots[0].timerange.start.hour == 9
    assert slots[0].timerange.end.hour == 17


def test_fixed_strategy_generates_regular_slots(scheduler: Scheduler) -> None:
    scheduler.add_strategy(FixedIntervalSlotStrategy(slot_size=timedelta(minutes=30)))
    scheduler.add_block(
        "demo",
        start=datetime(2026, 3, 23, 12, 0, tzinfo=UTC),
        end=datetime(2026, 3, 23, 13, 0, tzinfo=UTC),
    )

    slots = scheduler.get_slots("demo")
    blocked = TimeRange(
        start=datetime(2026, 3, 23, 12, 0, tzinfo=UTC),
        end=datetime(2026, 3, 23, 13, 0, tzinfo=UTC),
    )

    assert len(slots) == 14
    assert slots[0].timerange.start.hour == 9
    assert slots[-1].timerange.end.hour == 17
    assert all(not slot.timerange.overlaps(blocked) for slot in slots)


def test_overlap_conflict_is_rejected(scheduler: Scheduler) -> None:
    scheduler.book(
        "demo",
        start=datetime(2026, 3, 23, 10, 0, tzinfo=UTC),
        end=datetime(2026, 3, 23, 11, 0, tzinfo=UTC),
    )

    with pytest.raises(ConflictError):
        scheduler.book(
            "demo",
            start=datetime(2026, 3, 23, 10, 30, tzinfo=UTC),
            end=datetime(2026, 3, 23, 11, 30, tzinfo=UTC),
        )


def test_idempotent_booking_returns_existing_event(scheduler: Scheduler) -> None:
    first = scheduler.book(
        "demo",
        start=datetime(2026, 3, 23, 14, 0, tzinfo=UTC),
        end=datetime(2026, 3, 23, 15, 0, tzinfo=UTC),
        idempotency_key="abc",
    )
    second = scheduler.book(
        "demo",
        start=datetime(2026, 3, 23, 14, 0, tzinfo=UTC),
        end=datetime(2026, 3, 23, 15, 0, tzinfo=UTC),
        idempotency_key="abc",
    )

    assert first.event_id == second.event_id
    assert len(scheduler.repository.get_schedule("demo").events) == 1


def test_custom_rules_can_be_added(schedule_definition: ScheduleDefinition) -> None:
    repository = InMemoryScheduleRepository()
    repository.create_schedule(schedule_definition)
    scheduler = Scheduler(
        repository=repository,
        now_provider=lambda: datetime(2026, 3, 23, 8, 0, tzinfo=UTC),
    )
    scheduler.add_rule(LeadTimeRule(minimum_notice=timedelta(hours=2)))
    scheduler.add_rule(BufferBetweenBookingsRule(buffer=timedelta(minutes=15)))

    scheduler.book(
        "demo",
        start=datetime(2026, 3, 23, 11, 0, tzinfo=UTC),
        end=datetime(2026, 3, 23, 12, 0, tzinfo=UTC),
    )

    with pytest.raises(ConflictError):
        scheduler.book(
            "demo",
            start=datetime(2026, 3, 23, 12, 10, tzinfo=UTC),
            end=datetime(2026, 3, 23, 13, 0, tzinfo=UTC),
        )

    with pytest.raises(ValidationError):
        scheduler.book(
            "demo",
            start=datetime(2026, 3, 23, 9, 0, tzinfo=UTC),
            end=datetime(2026, 3, 23, 9, 30, tzinfo=UTC),
        )


def test_repository_optimistic_concurrency_hook(schedule_definition: ScheduleDefinition) -> None:
    repository = InMemoryScheduleRepository()
    state = repository.create_schedule(schedule_definition)
    updated = state.with_events(
        (
            Event(
                event_id="evt-1",
                timerange=TimeRange(
                    start=datetime(2026, 3, 23, 10, 0, tzinfo=UTC),
                    end=datetime(2026, 3, 23, 11, 0, tzinfo=UTC),
                ),
            ),
        )
    )
    repository.save_schedule(updated, expected_version=0)

    with pytest.raises(ConcurrencyError):
        repository.save_schedule(updated, expected_version=0)


def test_naive_datetime_is_rejected(scheduler: Scheduler) -> None:
    with pytest.raises(ValidationError):
        scheduler.book(
            "demo",
            start=datetime(2026, 3, 23, 10, 0),
            end=datetime(2026, 3, 23, 11, 0),
        )
