from datetime import UTC, datetime, timedelta
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from slotify import InMemoryScheduleRepository, Scheduler
from slotify.domain import ScheduleDefinition, TimeRange
from slotify.exceptions import ConflictError, ValidationError
from slotify.rules import RuleContext


class BreakMax15Rule:
    def validate(self, schedule, event, context: RuleContext) -> None:
        if event.event_type == "break" and event.timerange.duration > timedelta(minutes=15):
            raise ValidationError("Break cannot be longer than 15 minutes")


def main() -> None:
    repository = InMemoryScheduleRepository()
    scheduler = Scheduler(repository=repository)
    scheduler.add_rule(BreakMax15Rule())
    schedule_id = "conflict-demo"

    repository.create_schedule(
        ScheduleDefinition(
            schedule_id=schedule_id,
            bounds=TimeRange(
                start=datetime(2026, 3, 23, 8, 0, tzinfo=UTC),
                end=datetime(2026, 3, 23, 23, 0, tzinfo=UTC),
            ),
        )
    )

    scheduler.book(
        schedule_id,
        start=datetime(2026, 3, 23, 10, 0, tzinfo=UTC),
        end=datetime(2026, 3, 23, 12, 0, tzinfo=UTC),
        event_type="work",
    )

    try:
        scheduler.book(
            schedule_id,
            start=datetime(2026, 3, 23, 11, 30, tzinfo=UTC),
            end=datetime(2026, 3, 23, 12, 30, tzinfo=UTC),
            event_type="lunch",
        )
    except ConflictError as exc:
        print("Overlap conflict:", exc)

    try:
        scheduler.book(
            schedule_id,
            start=datetime(2026, 3, 23, 16, 0, tzinfo=UTC),
            end=datetime(2026, 3, 23, 16, 30, tzinfo=UTC),
            event_type="break",
        )
    except ValidationError as exc:
        print("Custom rule:", exc)


if __name__ == "__main__":
    main()
