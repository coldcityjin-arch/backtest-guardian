"""Anchored walk-forward parameter evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .core import BacktestResult, CostModel, backtest, moving_average_signal


@dataclass(frozen=True)
class FoldResult:
    train_end: int
    test_end: int
    selected_window: int
    train_return: float
    test_result: BacktestResult


def walk_forward(
    prices: Sequence[float],
    windows: Sequence[int],
    initial_train: int,
    test_size: int,
    costs: CostModel | None = None,
) -> list[FoldResult]:
    """Tune on past data, then evaluate the untouched next block."""
    if initial_train < 2 or test_size < 1 or initial_train >= len(prices):
        raise ValueError("invalid train/test sizes")
    if not windows or any(w < 1 for w in windows):
        raise ValueError("windows must contain positive integers")
    folds: list[FoldResult] = []
    train_end = initial_train
    while train_end < len(prices):
        test_end = min(train_end + test_size, len(prices))
        train_prices = prices[:train_end]
        scores = {
            window: backtest(train_prices, moving_average_signal(train_prices, window), costs).total_return
            for window in windows
        }
        selected = max(windows, key=lambda window: (scores[window], -window))

        # Include historical context for indicators, but report only the test segment.
        context_start = max(0, train_end - selected)
        segment = prices[context_start:test_end]
        signals = moving_average_signal(segment, selected)
        boundary = train_end - context_start
        test_prices = segment[boundary - 1 :]
        test_signals = signals[boundary - 1 :]
        result = backtest(test_prices, test_signals, costs)
        folds.append(FoldResult(train_end, test_end, selected, scores[selected], result))
        train_end = test_end
    return folds

