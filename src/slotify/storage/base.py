from __future__ import annotations

from typing import Protocol

from slotify.domain import Event, ScheduleDefinition, ScheduleState


class ScheduleRepository(Protocol):
    def create_schedule(self, definition: ScheduleDefinition) -> ScheduleState:
        """Create and persist a new schedule."""

    def get_schedule(self, schedule_id: str) -> ScheduleState:
        """Return schedule state or raise if missing."""

    def save_schedule(self, schedule: ScheduleState, expected_version: int | None = None) -> ScheduleState:
        """Persist schedule changes with optional optimistic concurrency."""

    def find_event(self, schedule_id: str, event_id: str) -> Event | None:
        """Return event if present."""
