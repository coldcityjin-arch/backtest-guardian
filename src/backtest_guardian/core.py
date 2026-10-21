"""Backtest engine with explicit anti-look-ahead execution semantics."""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import fmean, pstdev
from typing import Sequence


@dataclass(frozen=True)
class CostModel:
    """Per-turnover trading costs in basis points."""

    commission_bps: float = 0.0
    slippage_bps: float = 0.0

    @property
    def rate(self) -> float:
        if self.commission_bps < 0 or self.slippage_bps < 0:
            raise ValueError("costs must be non-negative")
        return (self.commission_bps + self.slippage_bps) / 10_000.0


@dataclass(frozen=True)
class BacktestResult:
    equity: tuple[float, ...]
    returns: tuple[float, ...]
    positions: tuple[float, ...]
    turnover: float
    total_cost: float
    total_return: float
    max_drawdown: float
    annualized_sharpe: float


def moving_average_signal(prices: Sequence[float], window: int) -> list[float]:
    """Return a long/cash signal using only data available at each close."""
    if window < 1:
        raise ValueError("window must be positive")
    signal: list[float] = []
    running = 0.0
    for i, price in enumerate(prices):
        running += price
        if i >= window:
            running -= prices[i - window]
        if i + 1 < window:
            signal.append(0.0)
        else:
            signal.append(1.0 if price > running / window else 0.0)
    return signal


def backtest(
    prices: Sequence[float],
    signals: Sequence[float],
    costs: CostModel | None = None,
    periods_per_year: int = 252,
) -> BacktestResult:
    """Execute close-derived signals from the *next* bar onward.

    ``signals[t-1]`` controls exposure over ``prices[t-1] -> prices[t]``.
    This one-bar lag prevents same-close look-ahead.
    """
    if len(prices) != len(signals) or len(prices) < 2:
        raise ValueError("prices and signals must have equal length >= 2")
    if any(p <= 0 for p in prices):
        raise ValueError("prices must be positive")
    if any(not 0.0 <= s <= 1.0 for s in signals):
        raise ValueError("signals must be between 0 and 1")

    model = costs or CostModel()
    rate = model.rate
    equity = [1.0]
    strategy_returns: list[float] = []
    executed_positions = [0.0]
    turnover = 0.0
    total_cost = 0.0
    previous_position = 0.0

    for t in range(1, len(prices)):
        position = float(signals[t - 1])
        traded = abs(position - previous_position)
        cost = traded * rate
        asset_return = prices[t] / prices[t - 1] - 1.0
        net_return = position * asset_return - cost
        equity.append(equity[-1] * (1.0 + net_return))
        strategy_returns.append(net_return)
        executed_positions.append(position)
        turnover += traded
        total_cost += equity[-2] * cost
        previous_position = position

    peak = equity[0]
    max_drawdown = 0.0
    for value in equity:
        peak = max(peak, value)
        max_drawdown = min(max_drawdown, value / peak - 1.0)
    volatility = pstdev(strategy_returns)
    sharpe = 0.0 if volatility == 0 else fmean(strategy_returns) / volatility * sqrt(periods_per_year)
    return BacktestResult(
        equity=tuple(equity),
        returns=tuple(strategy_returns),
        positions=tuple(executed_positions),
        turnover=turnover,
        total_cost=total_cost,
        total_return=equity[-1] - 1.0,
        max_drawdown=max_drawdown,
        annualized_sharpe=sharpe,
    )

