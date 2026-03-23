# slotify

English version: [README.en.md](README.en.md).

`slotify` состоит из двух слоев:

- `slotify`: framework-agnostic ядро для расписаний, слотов, событий и правил
- `slotify_django`: опциональный Django companion app с моделями, admin и сервисами

## Установка

Только ядро:

```bash
python -m pip install slotify-engine
```

С Django-поддержкой:

```bash
python -m pip install 'slotify-engine[django]'
```

Для локальной разработки:

```bash
python -m pip install -e .[dev]
```

## Что есть в пакете

- UTC-first модель вычислений
- source of truth через события
- derived free slots с корректным split / merge
- pluggable rules engine
- in-memory repository
- reusable Django app для быстрого старта через admin

## Django quickstart

1. Добавь `slotify_django` в `INSTALLED_APPS`.
2. Выполни `python manage.py migrate`.
3. Создай в admin:
   - `Schedule`
   - `AvailabilityRule`
   - `ScheduleEvent`
4. Получай свободные слоты через `slotify_django.services.generate_slots(...)`.

## Базовые модели Django слоя

- `slotify_django.Schedule`
- `slotify_django.AvailabilityRule`
- `slotify_django.ScheduleEvent`

## Ограничения v1

- межпроцессная блокировка не реализована в core
- полноценный RRULE engine отложен
- recurring availability в Django слое разворачивается по дням на сервисном уровне

## Документация

- [README.en.md](README.en.md)
- [docs/guide.ru.md](docs/guide.ru.md)
- [docs/guide.en.md](docs/guide.en.md)
- [docs/integration-notes.ru.md](docs/integration-notes.ru.md)
- [docs/integration-notes.en.md](docs/integration-notes.en.md)
