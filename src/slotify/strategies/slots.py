from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from slotify.domain import ScheduleState, Slot, SlotStatus, TimeRange
from slotify.exceptions import ValidationError
from slotify.strategies.base import SlotGenerationStrategy
from slotify.strategies.helpers import free_segments, merge_compatible_slots


@dataclass(frozen=True, slots=True)
class DynamicFreeSlotStrategy(SlotGenerationStrategy):
    merge_adjacent: bool = True

    def generate(self, schedule: ScheduleState, within: TimeRange | None = None) -> list[Slot]:
        slots = [
            Slot(
                timerange=segment,
                status=SlotStatus.FREE,
                schedule_id=schedule.definition.schedule_id,
            )
            for segment in free_segments(schedule, within)
            if segment.duration >= schedule.definition.min_slot_size
        ]
        if self.merge_adjacent and schedule.definition.merge_adjacent_free_slots:
            return merge_compatible_slots(slots)
        return slots


@dataclass(frozen=True, slots=True)
class FixedIntervalSlotStrategy(SlotGenerationStrategy):
    slot_size: timedelta | None = None

    def generate(self, schedule: ScheduleState, within: TimeRange | None = None) -> list[Slot]:
        duration = self.slot_size or schedule.definition.slot_size
        if duration <= timedelta(0):
            msg = "slot_size must be positive"
            raise ValidationError(msg)
        slots: list[Slot] = []
        for segment in free_segments(schedule, within):
            cursor = segment.start
            while cursor + duration <= segment.end:
                slots.append(
                    Slot(
                        timerange=TimeRange(cursor, cursor + duration),
                        status=SlotStatus.FREE,
                        schedule_id=schedule.definition.schedule_id,
                    )
                )
                cursor += duration
        return slots
