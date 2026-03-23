# slotify

English version: [README.en.md](README.en.md).

`slotify` это headless Python-библиотека для работы с расписаниями, временными диапазонами, таймслотами, бронированием, блокировками и правилами планирования.

Она проектировалась как встраиваемый scheduling engine, а не как конечное приложение.

## Для чего подходит

- Django / FastAPI / Flask backend
- CLI-утилиты
- микросервисы
- внутренние scheduling-сервисы
- reusable open-source проекты

## Что есть в v0.1

- UTC-first модель вычислений с timezone-aware API
- immutable `TimeRange` и typed domain-модель
- source of truth через `Event`, derived representation через `Slot`
- pluggable rules engine
- dynamic и fixed slot generation strategies
- split / merge свободных интервалов
- in-memory repository
- optimistic concurrency hooks на уровне storage abstraction
- простой API и расширяемый command/object API

## Быстрый старт

```python
from datetime import UTC, datetime, timedelta

from slotify import InMemoryScheduleRepository, Scheduler
from slotify.domain import ScheduleDefinition, TimeRange

repository = InMemoryScheduleRepository()
scheduler = Scheduler(repository=repository)

repository.create_schedule(
    ScheduleDefinition(
        schedule_id="demo",
        bounds=TimeRange(
            start=datetime(2026, 3, 23, 9, 0, tzinfo=UTC),
            end=datetime(2026, 3, 23, 17, 0, tzinfo=UTC),
        ),
        timezone="Europe/Moscow",
        slot_size=timedelta(minutes=30),
    )
)

booking = scheduler.book(
    schedule_id="demo",
    start=datetime(2026, 3, 23, 10, 0, tzinfo=UTC),
    end=datetime(2026, 3, 23, 11, 0, tzinfo=UTC),
)

slots = scheduler.get_slots("demo")
```

## Ключевые идеи

- Источник истины: события и ограничения.
- Таймслоты вычисляются стратегиями, а не хранятся как единственная правда.
- Ядро не знает ничего о CRM, специалистах, клиентах или заказах.
- Предметный смысл должен жить в `metadata`, `tags` и внешних адаптерах.

## Структура пакета

```text
src/slotify/
  domain/
  engine/
  rules/
  storage/
  strategies/
  adapters/
  exceptions.py
```

## Ограничения v1

- межпроцессная блокировка не реализована в core
- полноценный RRULE engine отложен
- ORM-интеграции пока представлены архитектурными заготовками, а не готовыми адаптерами

## Разработка

```bash
python -m pip install -e .[dev]
pytest
```

## Документация

- Английский обзор: [README.en.md](README.en.md)
- Русский guide: [docs/guide.ru.md](docs/guide.ru.md)
- English guide: [docs/guide.en.md](docs/guide.en.md)
- Russian integration notes: [docs/integration-notes.ru.md](docs/integration-notes.ru.md)
- English integration notes: [docs/integration-notes.en.md](docs/integration-notes.en.md)

## Лицензия

Рекомендуемая лицензия: MIT. См. [LICENSE](LICENSE).
