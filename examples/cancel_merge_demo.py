from datetime import UTC, datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from slotify import InMemoryScheduleRepository, Scheduler
from slotify.domain import ScheduleDefinition, TimeRange


def show_slots(label: str, scheduler: Scheduler, schedule_id: str) -> None:
    print(f"\n{label}")
    for slot in scheduler.get_slots(schedule_id):
        print(f"FREE {slot.timerange.start:%H:%M} - {slot.timerange.end:%H:%M}")


def main() -> None:
    repository = InMemoryScheduleRepository()
    scheduler = Scheduler(repository=repository)
    schedule_id = "cancel-demo"

    repository.create_schedule(
        ScheduleDefinition(
            schedule_id=schedule_id,
            bounds=TimeRange(
                start=datetime(2026, 3, 23, 8, 0, tzinfo=UTC),
                end=datetime(2026, 3, 23, 23, 0, tzinfo=UTC),
            ),
        )
    )

    lunch = scheduler.book(
        schedule_id,
        start=datetime(2026, 3, 23, 14, 0, tzinfo=UTC),
        end=datetime(2026, 3, 23, 15, 0, tzinfo=UTC),
        event_type="lunch",
    )
    show_slots("With lunch inside the day", scheduler, schedule_id)

    scheduler.cancel(schedule_id, lunch.event_id)
    show_slots("After cancel -> adjacent free slots merge back", scheduler, schedule_id)


if __name__ == "__main__":
    main()
