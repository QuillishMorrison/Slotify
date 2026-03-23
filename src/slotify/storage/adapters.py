from __future__ import annotations

from dataclasses import dataclass

from slotify.storage.base import ScheduleRepository


@dataclass(frozen=True, slots=True)
class SqlAlchemyAdapterHint:
    """Placeholder describing intended adapter surface for future releases."""

    repository_protocol: type[ScheduleRepository] = ScheduleRepository


@dataclass(frozen=True, slots=True)
class DjangoAdapterHint:
    """Placeholder describing intended adapter surface for future releases."""

    repository_protocol: type[ScheduleRepository] = ScheduleRepository
