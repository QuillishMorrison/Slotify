from __future__ import annotations

from typing import Protocol

from slotify.domain import ScheduleState, Slot, TimeRange


class SlotGenerationStrategy(Protocol):
    def generate(self, schedule: ScheduleState, within: TimeRange | None = None) -> list[Slot]:
        """Generate derived slots."""
