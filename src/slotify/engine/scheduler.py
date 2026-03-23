from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Callable
from uuid import uuid4

from slotify.domain import Event, ScheduleState, Slot, TimeRange, to_utc
from slotify.engine.commands import AddEventCommand, AddRuleCommand, BookCommand, CancelCommand
from slotify.exceptions import EventNotFoundError, ValidationError
from slotify.rules import (
    EventIdUniquenessRule,
    NoOverlapRule,
    Rule,
    RuleContext,
    RuleEngine,
    StartBeforeEndRule,
    WithinBoundsRule,
)
from slotify.storage.base import ScheduleRepository
from slotify.strategies import DynamicFreeSlotStrategy, SlotGenerationStrategy


@dataclass(slots=True)
class Scheduler:
    repository: ScheduleRepository
    slot_strategy: SlotGenerationStrategy = field(default_factory=DynamicFreeSlotStrategy)
    now_provider: Callable[[], datetime] = field(default_factory=lambda: (lambda: datetime.now(UTC)))
    rule_engine: RuleEngine = field(default_factory=RuleEngine)

    def __post_init__(self) -> None:
        if not self.rule_engine.rules:
            self.rule_engine.rules.extend(
                [
                    StartBeforeEndRule(),
                    WithinBoundsRule(),
                    EventIdUniquenessRule(),
                    NoOverlapRule(),
                ]
            )

    def add_rule(self, rule: Rule) -> None:
        self.rule_engine.add_rule(rule)

    def add_strategy(self, strategy: SlotGenerationStrategy) -> None:
        self.slot_strategy = strategy

    def add_event(self, event: Event, schedule_id: str | None = None) -> Event:
        actual_schedule_id = schedule_id or event.metadata.get("schedule_id")
        if actual_schedule_id is None:
            msg = "schedule_id is required"
            raise ValidationError(msg)
        schedule = self.repository.get_schedule(actual_schedule_id)
        self._validate(schedule, event, operation="add_event")
        new_state = schedule.with_events(schedule.events + (event,))
        self.repository.save_schedule(new_state, expected_version=schedule.version)
        return event

    def book(
        self,
        schedule_id: str,
        start: datetime,
        end: datetime,
        *,
        event_type: str = "booking",
        metadata: dict[str, Any] | None = None,
        tags: frozenset[str] | None = None,
        idempotency_key: str | None = None,
        blocks_availability: bool = True,
    ) -> Event:
        schedule = self.repository.get_schedule(schedule_id)
        if idempotency_key is not None:
            existing = self._find_by_idempotency_key(schedule, idempotency_key)
            if existing is not None:
                return existing
        event = Event(
            event_id=str(uuid4()),
            timerange=TimeRange(start=start, end=end),
            event_type=event_type,
            metadata=dict(metadata or {}),
            tags=tags or frozenset(),
            idempotency_key=idempotency_key,
            blocks_availability=blocks_availability,
        )
        self._validate(schedule, event, operation="book")
        new_state = schedule.with_events(schedule.events + (event,))
        self.repository.save_schedule(new_state, expected_version=schedule.version)
        return event

    def cancel(self, schedule_id: str, event_id: str) -> Event:
        schedule = self.repository.get_schedule(schedule_id)
        updated_events = []
        cancelled: Event | None = None
        for event in schedule.events:
            if event.event_id == event_id:
                cancelled = event.cancel()
                updated_events.append(cancelled)
            else:
                updated_events.append(event)
        if cancelled is None:
            msg = f"event not found: {event_id}"
            raise EventNotFoundError(msg)
        new_state = schedule.with_events(tuple(updated_events))
        self.repository.save_schedule(new_state, expected_version=schedule.version)
        return cancelled

    def add_block(
        self,
        schedule_id: str,
        start: datetime,
        end: datetime,
        *,
        metadata: dict[str, Any] | None = None,
        tags: frozenset[str] | None = None,
    ) -> Event:
        return self.book(
            schedule_id=schedule_id,
            start=start,
            end=end,
            event_type="block",
            metadata={"role": "block", **(metadata or {})},
            tags=tags,
        )

    def get_slots(self, schedule_id: str, within: TimeRange | None = None) -> list[Slot]:
        schedule = self.repository.get_schedule(schedule_id)
        return self.slot_strategy.generate(schedule, within=within)

    def generate_slots(self, schedule_id: str, within: TimeRange | None = None) -> list[Slot]:
        return self.get_slots(schedule_id, within=within)

    def evaluate(self, schedule: ScheduleState, context: RuleContext | None = None) -> list[Slot]:
        _ = context
        return self.slot_strategy.generate(schedule)

    def apply(self, command: BookCommand | CancelCommand | AddEventCommand | AddRuleCommand) -> Any:
        if isinstance(command, BookCommand):
            return self.book(
                schedule_id=command.schedule_id,
                start=command.start,
                end=command.end,
                event_type=command.event_type,
                metadata=command.metadata,
                tags=command.tags,
                idempotency_key=command.idempotency_key,
            )
        if isinstance(command, CancelCommand):
            return self.cancel(schedule_id=command.schedule_id, event_id=command.event_id)
        if isinstance(command, AddEventCommand):
            return self.add_event(command.event, schedule_id=command.schedule_id)
        if isinstance(command, AddRuleCommand):
            self.add_rule(command.rule)
            return None
        msg = f"unsupported command: {type(command)!r}"
        raise ValidationError(msg)

    def _find_by_idempotency_key(self, schedule: ScheduleState, key: str) -> Event | None:
        for event in schedule.events:
            if event.idempotency_key == key and event.is_active:
                return event
        return None

    def _validate(self, schedule: ScheduleState, event: Event, *, operation: str) -> None:
        context = RuleContext(now=self._current_time(), operation=operation)
        self.rule_engine.validate(schedule, event, context)

    def _current_time(self) -> datetime:
        return to_utc(self.now_provider())
