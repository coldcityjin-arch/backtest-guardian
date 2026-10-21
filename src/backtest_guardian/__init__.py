"""Backtest Guardian public API."""

from .core import BacktestResult, CostModel, backtest, moving_average_signal
from .validation import DataIssue, validate_prices
from .walkforward import FoldResult, walk_forward

__all__ = [
    "BacktestResult",
    "CostModel",
    "DataIssue",
    "FoldResult",
    "backtest",
    "moving_average_signal",
    "validate_prices",
    "walk_forward",
]

