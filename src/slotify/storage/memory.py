from __future__ import annotations

from copy import deepcopy

from slotify.domain import Event, ScheduleDefinition, ScheduleState
from slotify.exceptions import ConcurrencyError, EventNotFoundError, ScheduleNotFoundError


class InMemoryScheduleRepository:
    def __init__(self) -> None:
        self._schedules: dict[str, ScheduleState] = {}

    def create_schedule(self, definition: ScheduleDefinition) -> ScheduleState:
        state = ScheduleState(definition=definition)
        self._schedules[definition.schedule_id] = state
        return deepcopy(state)

    def get_schedule(self, schedule_id: str) -> ScheduleState:
        schedule = self._schedules.get(schedule_id)
        if schedule is None:
            msg = f"schedule not found: {schedule_id}"
            raise ScheduleNotFoundError(msg)
        return deepcopy(schedule)

    def save_schedule(self, schedule: ScheduleState, expected_version: int | None = None) -> ScheduleState:
        current = self._schedules.get(schedule.definition.schedule_id)
        if current is None:
            msg = f"schedule not found: {schedule.definition.schedule_id}"
            raise ScheduleNotFoundError(msg)
        if expected_version is not None and current.version != expected_version:
            msg = (
                f"schedule version mismatch for {schedule.definition.schedule_id}: "
                f"expected {expected_version}, actual {current.version}"
            )
            raise ConcurrencyError(msg)
        self._schedules[schedule.definition.schedule_id] = deepcopy(schedule)
        return deepcopy(schedule)

    def find_event(self, schedule_id: str, event_id: str) -> Event | None:
        schedule = self._schedules.get(schedule_id)
        if schedule is None:
            msg = f"schedule not found: {schedule_id}"
            raise ScheduleNotFoundError(msg)
        for event in schedule.events:
            if event.event_id == event_id:
                return deepcopy(event)
        return None

    def require_event(self, schedule_id: str, event_id: str) -> Event:
        event = self.find_event(schedule_id, event_id)
        if event is None:
            msg = f"event not found: {event_id}"
            raise EventNotFoundError(msg)
        return event
