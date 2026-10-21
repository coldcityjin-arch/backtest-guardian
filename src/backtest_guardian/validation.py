"""Input validation for ordered price observations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Sequence


@dataclass(frozen=True)
class DataIssue:
    row: int
    code: str
    message: str


def validate_prices(timestamps: Sequence[datetime], prices: Sequence[float]) -> list[DataIssue]:
    issues: list[DataIssue] = []
    if len(timestamps) != len(prices):
        return [DataIssue(-1, "length_mismatch", "timestamps and prices differ in length")]
    seen: set[datetime] = set()
    for i, (timestamp, price) in enumerate(zip(timestamps, prices)):
        if timestamp in seen:
            issues.append(DataIssue(i, "duplicate_timestamp", f"duplicate timestamp: {timestamp.isoformat()}"))
        seen.add(timestamp)
        if i and timestamp <= timestamps[i - 1]:
            issues.append(DataIssue(i, "non_monotonic_time", "timestamps must be strictly increasing"))
        if not isfinite(price):
            issues.append(DataIssue(i, "non_finite_price", "price must be finite"))
        elif price <= 0:
            issues.append(DataIssue(i, "non_positive_price", "price must be positive"))
    return issues

