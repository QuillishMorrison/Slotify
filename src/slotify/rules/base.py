from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Protocol

from slotify.domain import Event, ScheduleState


@dataclass(frozen=True, slots=True)
class RuleContext:
    now: datetime | None = None
    operation: str = "validate"
    payload: dict[str, Any] = field(default_factory=dict)


class Rule(Protocol):
    def validate(self, schedule: ScheduleState, event: Event, context: RuleContext) -> None:
        """Validate an event against schedule state."""
