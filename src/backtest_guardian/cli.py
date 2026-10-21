"""Command-line interface."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import datetime
from pathlib import Path

from .core import CostModel, backtest, moving_average_signal
from .validation import validate_prices
from .walkforward import walk_forward


def _load_csv(path: Path) -> tuple[list[datetime], list[float]]:
    timestamps: list[datetime] = []
    prices: list[float] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            timestamps.append(datetime.fromisoformat(row["timestamp"].replace("Z", "+00:00")))
            prices.append(float(row["close"]))
    return timestamps, prices


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit a moving-average backtest")
    parser.add_argument("csv", type=Path, help="CSV with timestamp and close columns")
    parser.add_argument("--window", type=int, default=20)
    parser.add_argument("--commission-bps", type=float, default=1.0)
    parser.add_argument("--slippage-bps", type=float, default=2.0)
    parser.add_argument("--walk-forward", action="store_true")
    parser.add_argument("--test-size", type=int, default=20)
    args = parser.parse_args(argv)

    timestamps, prices = _load_csv(args.csv)
    issues = validate_prices(timestamps, prices)
    if issues:
        print(json.dumps({"valid": False, "issues": [issue.__dict__ for issue in issues]}, indent=2))
        return 2
    costs = CostModel(args.commission_bps, args.slippage_bps)
    result = backtest(prices, moving_average_signal(prices, args.window), costs)
    payload: dict[str, object] = {
        "valid": True,
        "observations": len(prices),
        "total_return": result.total_return,
        "max_drawdown": result.max_drawdown,
        "annualized_sharpe": result.annualized_sharpe,
        "turnover": result.turnover,
        "total_cost": result.total_cost,
    }
    if args.walk_forward:
        initial = max(args.window + 2, len(prices) // 2)
        payload["walk_forward"] = [
            {
                "train_end": fold.train_end,
                "test_end": fold.test_end,
                "selected_window": fold.selected_window,
                "test_return": fold.test_result.total_return,
            }
            for fold in walk_forward(prices, sorted({max(2, args.window // 2), args.window, args.window * 2}), initial, args.test_size, costs)
        ]
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

