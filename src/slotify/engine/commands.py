from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from slotify.domain import Event
from slotify.rules import Rule


@dataclass(frozen=True, slots=True)
class BookCommand:
    schedule_id: str
    start: datetime
    end: datetime
    event_type: str = "booking"
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: frozenset[str] = field(default_factory=frozenset)
    idempotency_key: str | None = None


@dataclass(frozen=True, slots=True)
class CancelCommand:
    schedule_id: str
    event_id: str


@dataclass(frozen=True, slots=True)
class AddEventCommand:
    schedule_id: str
    event: Event


@dataclass(frozen=True, slots=True)
class AddRuleCommand:
    rule: Rule
