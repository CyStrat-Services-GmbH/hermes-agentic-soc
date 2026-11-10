"""Extension contract only. No production connector is enabled in this MVP."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class QueryScope:
    tenant_id: str
    start_utc: str
    end_utc: str
    max_results: int = 100


class ReadOnlyConnector(Protocol):
    """Future implementations must enforce read-only access server-side.

    A Python interface or query-string filter alone is not a security boundary.
    Integration tests, Hermes secret-scope wiring and vendor sources are required
    before promoting any technology registry entry from scaffold to mvp.
    """

    def query(self, scope: QueryScope, query: str) -> dict:
        ...
