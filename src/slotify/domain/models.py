from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import timedelta
from enum import StrEnum
from typing import Any

from slotify.domain.time import TimeRange


Metadata = dict[str, Any]


class EventStatus(StrEnum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class SlotStatus(StrEnum):
    FREE = "free"
    OCCUPIED = "occupied"


@dataclass(frozen=True, slots=True)
class Event:
    event_id: str
    timerange: TimeRange
    event_type: str = "booking"
    status: EventStatus = EventStatus.CONFIRMED
    blocks_availability: bool = True
    metadata: Metadata = field(default_factory=dict)
    tags: frozenset[str] = field(default_factory=frozenset)
    version: int = 0
    idempotency_key: str | None = None

    @property
    def is_active(self) -> bool:
        return self.status == EventStatus.CONFIRMED

    def cancel(self) -> Event:
        return replace(self, status=EventStatus.CANCELLED, version=self.version + 1)


@dataclass(frozen=True, slots=True)
class Slot:
    timerange: TimeRange
    status: SlotStatus
    schedule_id: str
    metadata: Metadata = field(default_factory=dict)
    tags: frozenset[str] = field(default_factory=frozenset)
    source_event_ids: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ScheduleDefinition:
    schedule_id: str
    bounds: TimeRange
    timezone: str = "UTC"
    slot_size: timedelta = timedelta(minutes=30)
    min_slot_size: timedelta = timedelta(minutes=15)
    allow_overbooking: bool = False
    merge_adjacent_free_slots: bool = True
    metadata: Metadata = field(default_factory=dict)
    tags: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True, slots=True)
class ScheduleState:
    definition: ScheduleDefinition
    events: tuple[Event, ...] = ()
    version: int = 0

    def with_events(self, events: tuple[Event, ...]) -> ScheduleState:
        return ScheduleState(definition=self.definition, events=events, version=self.version + 1)

    def active_events(self) -> tuple[Event, ...]:
        return tuple(event for event in self.events if event.is_active)
