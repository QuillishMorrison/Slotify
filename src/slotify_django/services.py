from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from slotify import InMemoryScheduleRepository, Scheduler
from slotify.domain import ScheduleDefinition, TimeRange

from slotify_django.models import AvailabilityRule, Schedule, ScheduleEvent


@dataclass(frozen=True, slots=True)
class DailyScheduleBundle:
    day: date
    schedule_id: str
    scheduler: Scheduler


def _combine(day: date, value: time, timezone: str) -> datetime:
    return datetime.combine(day, value, tzinfo=ZoneInfo(timezone))


def _daily_schedule_id(schedule: Schedule, day: date, rule: AvailabilityRule) -> str:
    return f"{schedule.slug}:{day.isoformat()}:{rule.id}"


def build_day_scheduler(schedule: Schedule, day: date) -> list[DailyScheduleBundle]:
    repository = InMemoryScheduleRepository()
    bundles: list[DailyScheduleBundle] = []
    day_events = list(
        schedule.active_events().filter(start__date__lte=day, end__date__gte=day)
    )

    for rule in schedule.active_rules().filter(weekday=day.weekday()):
        scheduler = Scheduler(repository=repository)
        schedule_id = _daily_schedule_id(schedule, day, rule)
        start_dt = _combine(day, rule.start_time, schedule.timezone)
        end_dt = _combine(day, rule.end_time, schedule.timezone)

        repository.create_schedule(
            ScheduleDefinition(
                schedule_id=schedule_id,
                bounds=TimeRange(start=start_dt, end=end_dt),
                timezone=schedule.timezone,
                slot_size=schedule.slot_size,
                min_slot_size=schedule.min_slot_size,
                allow_overbooking=schedule.allow_overbooking,
                metadata={"rule_id": rule.id, **rule.metadata},
            )
        )

        for event in day_events:
            scheduler.book(
                schedule_id=schedule_id,
                start=event.start,
                end=event.end,
                event_type=event.event_type,
                metadata={"title": event.title, **event.metadata},
                tags=frozenset(event.tags),
                blocks_availability=event.blocks_availability,
            )

        bundles.append(DailyScheduleBundle(day=day, schedule_id=schedule_id, scheduler=scheduler))

    return bundles


def generate_slots(schedule: Schedule, start: date, end: date):
    slots = []
    cursor = start
    while cursor <= end:
        for bundle in build_day_scheduler(schedule, cursor):
            slots.extend(bundle.scheduler.get_slots(bundle.schedule_id))
        cursor += timedelta(days=1)
    return sorted(slots, key=lambda slot: slot.timerange.start)


def validate_event(schedule: Schedule, *, start: datetime, end: datetime, event_type: str, metadata: dict | None = None, tags: list[str] | None = None, blocks_availability: bool = True) -> None:
    day = start.astimezone(ZoneInfo(schedule.timezone)).date()
    bundles = build_day_scheduler(schedule, day)
    if not bundles:
        msg = "No availability rule matches the requested day"
        raise ValueError(msg)
    last_error: Exception | None = None
    for bundle in bundles:
        try:
            bundle.scheduler.book(
                schedule_id=bundle.schedule_id,
                start=start,
                end=end,
                event_type=event_type,
                metadata=metadata or {},
                tags=frozenset(tags or []),
                blocks_availability=blocks_availability,
            )
            return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
    if last_error is not None:
        raise last_error
