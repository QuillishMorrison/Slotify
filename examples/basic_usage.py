from datetime import UTC, datetime, timedelta

from slotify import InMemoryScheduleRepository, Scheduler
from slotify.domain import ScheduleDefinition, TimeRange


def main() -> None:
    repository = InMemoryScheduleRepository()
    scheduler = Scheduler(repository=repository)

    repository.create_schedule(
        ScheduleDefinition(
            schedule_id="demo",
            bounds=TimeRange(
                start=datetime(2026, 3, 23, 9, 0, tzinfo=UTC),
                end=datetime(2026, 3, 23, 17, 0, tzinfo=UTC),
            ),
            timezone="UTC",
            slot_size=timedelta(minutes=30),
        )
    )

    scheduler.book(
        schedule_id="demo",
        start=datetime(2026, 3, 23, 10, 0, tzinfo=UTC),
        end=datetime(2026, 3, 23, 11, 0, tzinfo=UTC),
        metadata={"kind": "booking"},
    )

    for slot in scheduler.get_slots("demo"):
        print(slot)


if __name__ == "__main__":
    main()

