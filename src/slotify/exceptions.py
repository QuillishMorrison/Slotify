class SlotifyError(Exception):
    """Base exception for the package."""


class ValidationError(SlotifyError):
    """Raised when a rule or invariant is violated."""


class ConflictError(SlotifyError):
    """Raised when an operation conflicts with existing state."""


class ScheduleNotFoundError(SlotifyError):
    """Raised when the requested schedule cannot be found."""


class EventNotFoundError(SlotifyError):
    """Raised when the requested event cannot be found."""


class ConcurrencyError(SlotifyError):
    """Raised when optimistic concurrency checks fail."""
