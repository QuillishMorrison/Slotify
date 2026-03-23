from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from slotify.exceptions import ValidationError


def ensure_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        msg = "datetime must be timezone-aware"
        raise ValidationError(msg)
    return value


def to_utc(value: datetime) -> datetime:
    return ensure_aware(value).astimezone(UTC)


def to_timezone(value: datetime, timezone: str) -> datetime:
    return to_utc(value).astimezone(ZoneInfo(timezone))


@dataclass(frozen=True, slots=True)
class TimeRange:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        start = to_utc(self.start)
        end = to_utc(self.end)
        if start >= end:
            msg = "start must be earlier than end"
            raise ValidationError(msg)
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "end", end)

    @property
    def duration(self) -> timedelta:
        return self.end - self.start

    def overlaps(self, other: TimeRange) -> bool:
        return self.start < other.end and other.start < self.end

    def contains(self, other: TimeRange) -> bool:
        return self.start <= other.start and self.end >= other.end

    def touches(self, other: TimeRange) -> bool:
        return self.end == other.start or other.end == self.start

    def intersection(self, other: TimeRange) -> TimeRange | None:
        if not self.overlaps(other):
            return None
        return TimeRange(start=max(self.start, other.start), end=min(self.end, other.end))

    def subtract(self, other: TimeRange) -> list[TimeRange]:
        if not self.overlaps(other):
            return [self]
        parts: list[TimeRange] = []
        if self.start < other.start:
            parts.append(TimeRange(self.start, min(self.end, other.start)))
        if self.end > other.end:
            parts.append(TimeRange(max(self.start, other.end), self.end))
        return parts

    def shift(self, delta: timedelta) -> TimeRange:
        return TimeRange(self.start + delta, self.end + delta)
