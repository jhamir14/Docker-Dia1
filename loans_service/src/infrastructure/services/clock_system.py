from datetime import date
from ...domain.ports.clock import Clock


class SystemClock(Clock):
    def today(self) -> date:
        return date.today()