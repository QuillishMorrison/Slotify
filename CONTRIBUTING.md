# Contributing

Thanks for considering contributing to `slotify`.

## Development setup

```bash
python -m pip install -e .[dev]
pytest
```

## Contribution guidelines

- Keep the core framework-agnostic.
- Prefer composition over inheritance.
- Preserve timezone-aware behavior.
- Add tests for rule or strategy changes.
- Document architectural tradeoffs explicitly.

## Pull requests

- include focused tests
- keep public API changes documented
- avoid introducing business-domain assumptions into core types

