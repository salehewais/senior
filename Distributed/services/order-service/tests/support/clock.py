from datetime import UTC, datetime, timedelta


class FixedClock:
    def __init__(self) -> None:
        self.current = datetime(2026, 10, 8, 9, 0, tzinfo=UTC)

    def now(self) -> datetime:
        self.current = self.current + timedelta(seconds=1)
        return self.current

    def jump(self, delta: timedelta) -> None:
        """Move the clock without counting as a read. Used to expire access tokens."""
        self.current = self.current + delta
