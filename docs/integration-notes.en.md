# Integration Notes

## Core guarantees

- `TimeRange` calculations require aware datetimes
- intervals are normalized to UTC
- repositories get a version hook for optimistic concurrency
- idempotency is supported via `book(..., idempotency_key=...)`

## Backend responsibilities

- atomic persistence of state or event log
- transactional boundaries for concurrent booking flows
- cross-process locking or conflict retry policy
- optional unique indexes for idempotency keys

## Integration recommendations

- Django: run `get -> validate -> save` inside `transaction.atomic()`
- SQLAlchemy: use row versioning or `SELECT ... FOR UPDATE` where appropriate
- microservices: treat the core as a deterministic evaluator and keep contention management in storage/API layers
