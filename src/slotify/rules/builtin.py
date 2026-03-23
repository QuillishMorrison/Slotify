from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from slotify.domain import Event, ScheduleState, TimeRange
from slotify.exceptions import ConflictError, ValidationError
from slotify.rules.base import RuleContext


@dataclass(frozen=True, slots=True)
class StartBeforeEndRule:
    def validate(self, schedule: ScheduleState, event: Event, context: RuleContext) -> None:
        if event.timerange.start >= event.timerange.end:
            msg = "event start must be earlier than end"
            raise ValidationError(msg)


@dataclass(frozen=True, slots=True)
class WithinBoundsRule:
    def validate(self, schedule: ScheduleState, event: Event, context: RuleContext) -> None:
        if not schedule.definition.bounds.contains(event.timerange):
            msg = "event must be inside schedule bounds"
            raise ValidationError(msg)


@dataclass(frozen=True, slots=True)
class NoOverlapRule:
    def validate(self, schedule: ScheduleState, event: Event, context: RuleContext) -> None:
        if schedule.definition.allow_overbooking or not event.blocks_availability:
            return
        for existing in schedule.active_events():
            if existing.event_id == event.event_id or not existing.blocks_availability:
                continue
            if existing.timerange.overlaps(event.timerange):
                msg = f"event overlaps with existing event {existing.event_id}"
                raise ConflictError(msg)


@dataclass(frozen=True, slots=True)
class MinDurationRule:
    minimum: timedelta

    def validate(self, schedule: ScheduleState, event: Event, context: RuleContext) -> None:
        if event.timerange.duration < self.minimum:
            msg = f"event duration must be at least {self.minimum}"
            raise ValidationError(msg)


@dataclass(frozen=True, slots=True)
class MaxDurationRule:
    maximum: timedelta

    def validate(self, schedule: ScheduleState, event: Event, context: RuleContext) -> None:
        if event.timerange.duration > self.maximum:
            msg = f"event duration must be at most {self.maximum}"
            raise ValidationError(msg)


@dataclass(frozen=True, slots=True)
class NoPastBookingRule:
    def validate(self, schedule: ScheduleState, event: Event, context: RuleContext) -> None:
        now = context.now
        if now is None:
            return
        if event.timerange.start < now:
            msg = "event cannot start in the past"
            raise ValidationError(msg)


@dataclass(frozen=True, slots=True)
class LeadTimeRule:
    minimum_notice: timedelta

    def validate(self, schedule: ScheduleState, event: Event, context: RuleContext) -> None:
        now = context.now
        if now is None:
            return
        if event.timerange.start - now < self.minimum_notice:
            msg = f"event must satisfy lead time of {self.minimum_notice}"
            raise ValidationError(msg)


@dataclass(frozen=True, slots=True)
class BufferBetweenBookingsRule:
    buffer: timedelta

    def validate(self, schedule: ScheduleState, event: Event, context: RuleContext) -> None:
        if self.buffer <= timedelta(0) or not event.blocks_availability:
            return
        buffered_range = TimeRange(
            start=event.timerange.start - self.buffer,
            end=event.timerange.end + self.buffer,
        )
        for existing in schedule.active_events():
            if existing.event_id == event.event_id or not existing.blocks_availability:
                continue
            if existing.timerange.overlaps(buffered_range):
                msg = f"event violates required buffer with {existing.event_id}"
                raise ConflictError(msg)


@dataclass(frozen=True, slots=True)
class EventIdUniquenessRule:
    def validate(self, schedule: ScheduleState, event: Event, context: RuleContext) -> None:
        for existing in schedule.events:
            if existing.event_id == event.event_id and existing.version == event.version:
                msg = f"duplicate event id detected: {event.event_id}"
                raise ConflictError(msg)
