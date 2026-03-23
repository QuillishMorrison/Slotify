from __future__ import annotations

from slotify.domain import Event, ScheduleState, Slot, TimeRange


def active_blocking_events(schedule: ScheduleState, within: TimeRange | None = None) -> list[Event]:
    events = [event for event in schedule.active_events() if event.blocks_availability]
    if within is None:
        return sorted(events, key=lambda item: item.timerange.start)
    return sorted(
        [event for event in events if event.timerange.overlaps(within)],
        key=lambda item: item.timerange.start,
    )


def free_segments(schedule: ScheduleState, within: TimeRange | None = None) -> list[TimeRange]:
    bounds = within.intersection(schedule.definition.bounds) if within else schedule.definition.bounds
    if bounds is None:
        return []

    segments = [bounds]
    for event in active_blocking_events(schedule, bounds):
        next_segments: list[TimeRange] = []
        for segment in segments:
            next_segments.extend(segment.subtract(event.timerange))
        segments = next_segments
    return segments


def merge_compatible_slots(slots: list[Slot]) -> list[Slot]:
    if not slots:
        return []
    ordered = sorted(slots, key=lambda slot: slot.timerange.start)
    merged: list[Slot] = [ordered[0]]
    for slot in ordered[1:]:
        last = merged[-1]
        if (
            last.status == slot.status
            and last.timerange.end == slot.timerange.start
            and last.metadata == slot.metadata
            and last.tags == slot.tags
            and last.schedule_id == slot.schedule_id
        ):
            merged[-1] = Slot(
                timerange=TimeRange(last.timerange.start, slot.timerange.end),
                status=last.status,
                schedule_id=last.schedule_id,
                metadata=last.metadata,
                tags=last.tags,
                source_event_ids=last.source_event_ids + slot.source_event_ids,
            )
            continue
        merged.append(slot)
    return merged
