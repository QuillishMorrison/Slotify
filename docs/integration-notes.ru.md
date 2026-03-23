# Integration Notes

## Гарантии ядра

- все вычисления `TimeRange` выполняются на aware datetime
- интервалы нормализуются в UTC
- repository получает version hook для optimistic concurrency
- idempotency поддерживается на уровне `book(..., idempotency_key=...)`

## Что должен гарантировать backend

- атомарное сохранение state или event log
- транзакционные границы при конкурентном бронировании
- межпроцессную блокировку или conflict retry policy
- при необходимости уникальные индексы для idempotency keys

## Рекомендации по интеграции

- Django: выполнять `get -> validate -> save` внутри `transaction.atomic()`
- SQLAlchemy: использовать row versioning или `SELECT ... FOR UPDATE` там, где это допустимо
- microservices: считать core deterministic evaluator, а конфликтное управление реализовать на storage/API слое
