from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from slotify.domain.time import TimeRange


class RecurrencePolicy(Protocol):
    def expand(self, within: TimeRange) -> list[TimeRange]:
        """Expand recurrence occurrences inside the requested window."""


@dataclass(frozen=True, slots=True)
class NoRecurrence:
    start: datetime
    end: datetime

    def expand(self, within: TimeRange) -> list[TimeRange]:
        occurrence = TimeRange(self.start, self.end)
        match = occurrence.intersection(within)
        return [match] if match is not None else []

